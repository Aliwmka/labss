from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from sql_requests import (
    INSERT_ROOM_SQL,
    FETCH_ROOMS_SQL,
    DELETE_ROOM_SQL,
    EDIT_ROOM_SQL,
)

class Rooms:
    def __init__(self, parent_frame, db_connection):
        self.parent_frame = parent_frame
        self.create_rooms_form()
        self.db_connection = db_connection
    
    def create_rooms_form(self):
        labels = ['ID', 'Номер', 'Вместимость', 'Комфортность', 'Цена']
        self.room_entries = []
        for i, label in enumerate(labels[1:]):  # Пропускаем 'ID' для ввода данных
            ttk.Label(self.parent_frame, text=label).grid(row=i, column=0, padx=(10, 5), pady=5, sticky='e')
            entry = ttk.Entry(self.parent_frame)
            entry.grid(row=i, column=1, padx=(5, 10), pady=5, sticky='w')
            self.room_entries.append(entry)
        
        self.rooms_table = ttk.Treeview(self.parent_frame, columns=labels, show='headings')
        for label in labels:
            self.rooms_table.heading(label, text=label)
        self.rooms_table.column("#0", width=0, stretch=tk.NO)
        for col in labels:
            self.rooms_table.column(col, anchor=tk.CENTER, width=150)
        
        self.rooms_table.grid(row=len(labels), column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        
        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.rooms_table.yview)
        self.rooms_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=len(labels), column=3, sticky='ns')
        
        # Создаем фрейм для кнопок
        buttons_frame = ttk.Frame(self.parent_frame)
        buttons_frame.grid(row=len(labels) + 1, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        # Центрируем кнопки в фрейме
        buttons_frame.columnconfigure(0, weight=1)
        save_button = ttk.Button(buttons_frame, text="Сохранить", command=self.save_room)
        save_button.grid(row=0, column=1, padx=5, pady=5)
        
        edit_button = ttk.Button(buttons_frame, text="Изменить запись", command=self.edit_record)
        edit_button.grid(row=0, column=2, padx=5, pady=5)
        
        delete_button = ttk.Button(buttons_frame, text="Удалить запись", command=self.delete_record)
        delete_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Добавляем событие двойного щелчка
        self.rooms_table.bind("<Double-1>", self.fill_entries)
    
    def fill_entries(self, event):
        if not self.rooms_table.selection():
            return
        selected_item = self.rooms_table.selection()[0]
        values = self.rooms_table.item(selected_item, 'values')
        for entry, value in zip(self.room_entries, values[1:]):  # Пропускаем 'ID'
            entry.delete(0, tk.END)
            entry.insert(0, value)
    
    def save_room(self):
        data = [entry.get() for entry in self.room_entries]
        
        # Проверка обязательных полей
        if not data[0]:  # Номер обязателен
            messagebox.showwarning("Предупреждение", "Номер комнаты является обязательным полем!")
            return
        
        try:
            self.insert_room(data)
            self.show_rooms()
            self.clear_entries()
            messagebox.showinfo("Успех", "Номер успешно добавлен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить номер: {e}")
    
    def insert_room(self, data):
        cur = self.db_connection.cursor()
        cur.execute(INSERT_ROOM_SQL, data)
        self.db_connection.commit()
        cur.close()
    
    def show_rooms(self):
        rooms = self.fetch_rooms()
        for row in self.rooms_table.get_children():
            self.rooms_table.delete(row)
        for room in rooms:
            self.rooms_table.insert('', 'end', values=room)
    
    def fetch_rooms(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_ROOMS_SQL)
        rooms = cur.fetchall()
        cur.close()
        return rooms
    
    def delete_record(self):
        if not self.rooms_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        selected_item = self.rooms_table.selection()[0]
        room_id = self.rooms_table.item(selected_item, 'values')[0]
        room_number = self.rooms_table.item(selected_item, 'values')[1]
        
        # Подтверждение удаления
        result = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить номер '{room_number}'?\nВсе связанные бронирования также будут удалены."
        )
        
        if not result:
            return
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(DELETE_ROOM_SQL, (room_id,))
            self.db_connection.commit()
            cur.close()
            
            self.rooms_table.delete(selected_item)
            self.clear_entries()
            messagebox.showinfo("Успех", "Номер и все связанные бронирования успешно удалены!")
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить номер: {e}")
    
    def edit_record(self):
        if not self.rooms_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return
        
        selected_item = self.rooms_table.selection()[0]
        room_id = self.rooms_table.item(selected_item, 'values')[0]
        data = [entry.get() for entry in self.room_entries]
        
        # Проверка обязательных полей
        if not data[0]:  # Номер обязателен
            messagebox.showwarning("Предупреждение", "Номер комнаты является обязательным полем!")
            return
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(EDIT_ROOM_SQL, (*data, room_id))
            self.db_connection.commit()
            cur.close()
            self.show_rooms()
            self.clear_entries()
            messagebox.showinfo("Успех", "Данные номера успешно обновлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
    
    def clear_entries(self):
        for entry in self.room_entries:
            entry.delete(0, tk.END)