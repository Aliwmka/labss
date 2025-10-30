# bookings.py
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from sql_requests import (
    INSERT_BOOKING_SQL,
    FETCH_BOOKINGS_SQL,
    FETCH_CLIENTS_FOR_BOOKINGS_SQL,
    FETCH_ROOMS_FOR_BOOKINGS_SQL,
    DELETE_BOOKING_SQL,
    EDIT_BOOKING_SQL,
)

class Bookings:
    def __init__(self, parent_frame, db_connection, app=None):
        self.parent_frame = parent_frame
        self.db_connection = db_connection
        self.app = app
        self.create_bookings_form()
    
    def create_bookings_form(self):
        self.refresh_data()
        
        labels = ['ID', 'Клиент', 'Номер', 'Дата заселения', 'Дата выселения', 'Примечание']
        self.booking_entries = []
        
        # Поле со списком для клиентов
        ttk.Label(self.parent_frame, text='Клиент').grid(row=0, column=0, padx=(10, 5), pady=5, sticky='e')
        self.client_combobox = ttk.Combobox(self.parent_frame, state="readonly")
        self.client_combobox.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='w')
        self.booking_entries.append(self.client_combobox)
        
        # Поле со списком для номеров
        ttk.Label(self.parent_frame, text='Номер').grid(row=1, column=0, padx=(10, 5), pady=5, sticky='e')
        self.room_combobox = ttk.Combobox(self.parent_frame, state="readonly")
        self.room_combobox.grid(row=1, column=1, padx=(5, 10), pady=5, sticky='w')
        self.booking_entries.append(self.room_combobox)
        
        # Поля для дат
        ttk.Label(self.parent_frame, text='Дата заселения').grid(row=2, column=0, padx=(10, 5), pady=5, sticky='e')
        self.check_in_entry = DateEntry(self.parent_frame, date_pattern='y-mm-dd', locale='ru_RU')
        self.check_in_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky='w')
        self.booking_entries.append(self.check_in_entry)
        
        ttk.Label(self.parent_frame, text='Дата выселения').grid(row=3, column=0, padx=(10, 5), pady=5, sticky='e')
        self.check_out_entry = DateEntry(self.parent_frame, date_pattern='y-mm-dd', locale='ru_RU')
        self.check_out_entry.grid(row=3, column=1, padx=(5, 10), pady=5, sticky='w')
        self.booking_entries.append(self.check_out_entry)
        
        # Поле для примечания
        ttk.Label(self.parent_frame, text='Примечание').grid(row=4, column=0, padx=(10, 5), pady=5, sticky='e')
        self.note_entry = ttk.Entry(self.parent_frame)
        self.note_entry.grid(row=4, column=1, padx=(5, 10), pady=5, sticky='w')
        self.booking_entries.append(self.note_entry)
        
        self.bookings_table = ttk.Treeview(self.parent_frame, columns=labels, show='headings')
        for label in labels:
            self.bookings_table.heading(label, text=label)
        self.bookings_table.column("#0", width=0, stretch=tk.NO)
        for col in labels:
            self.bookings_table.column(col, anchor=tk.CENTER, width=150)
        
        self.bookings_table.grid(row=len(labels), column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        
        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.bookings_table.yview)
        self.bookings_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=len(labels), column=3, sticky='ns')
        
        # Создаем фрейм для кнопок
        buttons_frame = ttk.Frame(self.parent_frame)
        buttons_frame.grid(row=len(labels) + 1, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        # Центрируем кнопки в фрейме
        buttons_frame.columnconfigure(0, weight=1)
        save_button = ttk.Button(buttons_frame, text="Сохранить", command=self.save_booking)
        save_button.grid(row=0, column=1, padx=5, pady=5)
        
        edit_button = ttk.Button(buttons_frame, text="Изменить запись", command=self.edit_record)
        edit_button.grid(row=0, column=2, padx=5, pady=5)
        
        delete_button = ttk.Button(buttons_frame, text="Удалить запись", command=self.delete_record)
        delete_button.grid(row=0, column=3, padx=5, pady=5)
        
        refresh_button = ttk.Button(buttons_frame, text="Обновить", command=self.refresh_data)
        refresh_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.bookings_table.bind("<Double-1>", self.fill_entries)
    
    def refresh_data(self):
        """Обновление данных клиентов и номеров"""
        self.clients = self.fetch_clients()
        self.rooms = self.fetch_rooms()
        
        if hasattr(self, 'client_combobox'):
            self.client_combobox['values'] = [f"{client[1]} {client[2]} {client[3]}" for client in self.clients]
        
        if hasattr(self, 'room_combobox'):
            self.room_combobox['values'] = [f"{room[1]} ({room[2]})" for room in self.rooms]
    
    def fill_entries(self, event):
        if not self.bookings_table.selection():
            return
        selected_item = self.bookings_table.selection()[0]
        values = self.bookings_table.item(selected_item, 'values')
        self.client_combobox.set(values[1])  # Заполняем поле клиента
        self.room_combobox.set(values[2])    # Заполняем поле номера
        
        # Заполняем даты и примечание
        self.check_in_entry.set_date(values[3])
        if values[4]:
            self.check_out_entry.set_date(values[4])
        else:
            self.check_out_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        if values[5]:
            self.note_entry.insert(0, values[5])
    
    def save_booking(self):
        data = [
            self.client_combobox.get(),
            self.room_combobox.get(),
            self.check_in_entry.get(),
            self.check_out_entry.get(),
            self.note_entry.get()
        ]
        
        if not data[0] or not data[1] or not data[2]:
            messagebox.showwarning("Предупреждение", "Клиент, номер и дата заселения являются обязательными полями!")
            return
        
        try:
            self.insert_booking(data)
            self.show_bookings()
            self.clear_entries()
            messagebox.showinfo("Успех", "Бронирование успешно добавлено!")
            
            # Обновляем данные в фильтрах
            if self.app and hasattr(self.app, 'data_filter'):
                self.app.data_filter.refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить бронирование: {e}")
    
    def insert_booking(self, data):
        client_name = data[0]
        room_info = data[1]
        
        # Находим ID клиента и номера по их данным
        client_id = next(client[0] for client in self.clients if f"{client[1]} {client[2]} {client[3]}" == client_name)
        room_id = next(room[0] for room in self.rooms if f"{room[1]} ({room[2]})" == room_info)
        
        cur = self.db_connection.cursor()
        cur.execute(INSERT_BOOKING_SQL, (client_id, room_id, data[2], data[3], data[4]))
        self.db_connection.commit()
        cur.close()
    
    def show_bookings(self):
        bookings = self.fetch_bookings()
        for row in self.bookings_table.get_children():
            self.bookings_table.delete(row)
        for booking in bookings:
            client_name = next(f"{client[1]} {client[2]} {client[3]}" for client in self.clients if client[0] == booking[1])
            room_info = next(f"{room[1]} ({room[2]})" for room in self.rooms if room[0] == booking[2])
            self.bookings_table.insert('', 'end',
                                      values=(booking[0], client_name, room_info, *booking[3:]))
    
    def fetch_bookings(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_BOOKINGS_SQL)
        bookings = cur.fetchall()
        cur.close()
        return bookings
    
    def fetch_clients(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_CLIENTS_FOR_BOOKINGS_SQL)
        clients = cur.fetchall()
        cur.close()
        return clients
    
    def fetch_rooms(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_ROOMS_FOR_BOOKINGS_SQL)
        rooms = cur.fetchall()
        cur.close()
        return rooms
    
    def delete_record(self):
        if not self.bookings_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        selected_item = self.bookings_table.selection()[0]
        booking_id = self.bookings_table.item(selected_item, 'values')[0]
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(DELETE_BOOKING_SQL, (booking_id,))
            self.db_connection.commit()
            cur.close()
            
            self.bookings_table.delete(selected_item)
            self.clear_entries()
            messagebox.showinfo("Успех", "Бронирование успешно удалено!")
            
            # Обновляем данные в фильтрах
            if self.app and hasattr(self.app, 'data_filter'):
                self.app.data_filter.refresh_data()
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить бронирование: {e}")
    
    def edit_record(self):
        if not self.bookings_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return
        
        selected_item = self.bookings_table.selection()[0]
        booking_id = self.bookings_table.item(selected_item, 'values')[0]
        data = [
            self.client_combobox.get(),
            self.room_combobox.get(),
            self.check_in_entry.get(),
            self.check_out_entry.get(),
            self.note_entry.get()
        ]
        
        if not data[0] or not data[1] or not data[2]:
            messagebox.showwarning("Предупреждение", "Клиент, номер и дата заселения являются обязательными полями!")
            return
        
        try:
            client_name = data[0]
            room_info = data[1]
            
            # Находим ID клиента и номера по их данным
            client_id = next(client[0] for client in self.clients if f"{client[1]} {client[2]} {client[3]}" == client_name)
            room_id = next(room[0] for room in self.rooms if f"{room[1]} ({room[2]})" == room_info)
            
            cur = self.db_connection.cursor()
            cur.execute(EDIT_BOOKING_SQL, (client_id, room_id, data[2], data[3], data[4], booking_id))
            self.db_connection.commit()
            cur.close()
            self.show_bookings()
            self.clear_entries()
            messagebox.showinfo("Успех", "Данные бронирования успешно обновлены!")
            
            # Обновляем данные в фильтрах
            if self.app and hasattr(self.app, 'data_filter'):
                self.app.data_filter.refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
    
    def clear_entries(self):
        for entry in self.booking_entries:
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            elif isinstance(entry, DateEntry):
                entry.delete(0, tk.END)
            else:
                entry.delete(0, tk.END)