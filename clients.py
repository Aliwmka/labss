# clients.py
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from sql_requests import (
    INSERT_CLIENT_SQL,
    FETCH_CLIENTS_SQL,
    DELETE_CLIENT_SQL,
    EDIT_CLIENT_SQL,
)

class Clients:
    def __init__(self, parent_frame, db_connection, app=None):
        self.parent_frame = parent_frame
        self.db_connection = db_connection
        self.app = app
        self.create_clients_form()
    
    def create_clients_form(self):
        labels = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Паспортные данные', 'Комментарий']
        self.client_entries = []
        for i, label in enumerate(labels[1:]):  # Пропускаем 'ID' для ввода данных
            ttk.Label(self.parent_frame, text=label).grid(row=i, column=0, padx=(10, 5), pady=5, sticky='e')
            entry = ttk.Entry(self.parent_frame)
            entry.grid(row=i, column=1, padx=(5, 10), pady=5, sticky='w')
            self.client_entries.append(entry)
        
        self.clients_table = ttk.Treeview(self.parent_frame, columns=labels, show='headings')
        for label in labels:
            self.clients_table.heading(label, text=label)
        self.clients_table.column("#0", width=0, stretch=tk.NO)
        for col in labels:
            self.clients_table.column(col, anchor=tk.CENTER, width=150)
        
        self.clients_table.grid(row=len(labels), column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        
        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.clients_table.yview)
        self.clients_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=len(labels), column=3, sticky='ns')
        
        # Создаем фрейм для кнопок
        buttons_frame = ttk.Frame(self.parent_frame)
        buttons_frame.grid(row=len(labels) + 1, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        # Центрируем кнопки в фрейме
        buttons_frame.columnconfigure(0, weight=1)
        save_button = ttk.Button(buttons_frame, text="Сохранить", command=self.save_client)
        save_button.grid(row=0, column=1, padx=5, pady=5)
        
        edit_button = ttk.Button(buttons_frame, text="Изменить запись", command=self.edit_record)
        edit_button.grid(row=0, column=2, padx=5, pady=5)
        
        delete_button = ttk.Button(buttons_frame, text="Удалить запись", command=self.delete_record)
        delete_button.grid(row=0, column=3, padx=5, pady=5)
        
        refresh_button = ttk.Button(buttons_frame, text="Обновить", command=self.show_clients)
        refresh_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Добавляем событие двойного щелчка
        self.clients_table.bind("<Double-1>", self.fill_entries)
    
    def fill_entries(self, event):
        if not self.clients_table.selection():
            return
        selected_item = self.clients_table.selection()[0]
        values = self.clients_table.item(selected_item, 'values')
        for entry, value in zip(self.client_entries, values[1:]):  # Пропускаем 'ID'
            entry.delete(0, tk.END)
            entry.insert(0, value)
    
    def save_client(self):
        data = [entry.get() for entry in self.client_entries]
        
        # Проверка обязательных полей
        if not data[0] or not data[1]:  # Фамилия и Имя обязательны
            messagebox.showwarning("Предупреждение", "Фамилия и Имя являются обязательными полями!")
            return
        
        try:
            self.insert_client(data)
            self.show_clients()
            self.clear_entries()
            messagebox.showinfo("Успех", "Клиент успешно добавлен!")
            
            # Обновляем данные в других модулях
            if self.app:
                if hasattr(self.app, 'bookings'):
                    self.app.bookings.refresh_data()
                if hasattr(self.app, 'data_filter'):
                    self.app.data_filter.refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить клиента: {e}")
    
    def insert_client(self, data):
        cur = self.db_connection.cursor()
        cur.execute(INSERT_CLIENT_SQL, data)
        self.db_connection.commit()
        cur.close()
    
    def show_clients(self):
        clients = self.fetch_clients()
        for row in self.clients_table.get_children():
            self.clients_table.delete(row)
        for client in clients:
            self.clients_table.insert('', 'end', values=client)
    
    def fetch_clients(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_CLIENTS_SQL)
        clients = cur.fetchall()
        cur.close()
        return clients
    
    def delete_record(self):
        if not self.clients_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        selected_item = self.clients_table.selection()[0]
        client_id = self.clients_table.item(selected_item, 'values')[0]
        client_name = f"{self.clients_table.item(selected_item, 'values')[1]} {self.clients_table.item(selected_item, 'values')[2]}"
        
        # Подтверждение удаления
        result = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить клиента '{client_name}'?\nВсе связанные бронирования также будут удалены."
        )
        
        if not result:
            return
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(DELETE_CLIENT_SQL, (client_id,))
            self.db_connection.commit()
            cur.close()
            
            self.clients_table.delete(selected_item)
            self.clear_entries()
            messagebox.showinfo("Успех", "Клиент и все связанные бронирования успешно удалены!")
            
            # Обновляем данные в других модулях
            if self.app:
                if hasattr(self.app, 'bookings'):
                    self.app.bookings.refresh_data()
                    self.app.bookings.show_bookings()
                if hasattr(self.app, 'data_filter'):
                    self.app.data_filter.refresh_data()
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить клиента: {e}")
    
    def edit_record(self):
        if not self.clients_table.selection():
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return
        
        selected_item = self.clients_table.selection()[0]
        client_id = self.clients_table.item(selected_item, 'values')[0]
        data = [entry.get() for entry in self.client_entries]
        
        # Проверка обязательных полей
        if not data[0] or not data[1]:  # Фамилия и Имя обязательны
            messagebox.showwarning("Предупреждение", "Фамилия и Имя являются обязательными полями!")
            return
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(EDIT_CLIENT_SQL, (*data, client_id))
            self.db_connection.commit()
            cur.close()
            self.show_clients()
            self.clear_entries()
            messagebox.showinfo("Успех", "Данные клиента успешно обновлены!")
            
            # Обновляем данные в других модулях
            if self.app:
                if hasattr(self.app, 'bookings'):
                    self.app.bookings.refresh_data()
                    self.app.bookings.show_bookings()
                if hasattr(self.app, 'data_filter'):
                    self.app.data_filter.refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
    
    def clear_entries(self):
        for entry in self.client_entries:
            entry.delete(0, tk.END)