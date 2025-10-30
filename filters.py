# filters.py
from tkinter import ttk
from tkcalendar import DateEntry
from export import export_to_word, export_to_excel
from import_data import import_from_excel, import_from_word
from tkinter import messagebox
from sql_requests import (
    LOAD_CLIENTS_FOR_FILTER_SQL,
    LOAD_ROOMS_FOR_FILTER_SQL,
    CLIENT_FILTER_SQL,
    ROOM_FILTER_SQL,
    APPLY_FILTERS_SQL,
    INSERT_BOOKING_SQL,
    FETCH_CLIENTS_FOR_BOOKINGS_SQL,
    FETCH_ROOMS_FOR_BOOKINGS_SQL,
)

class DataFilter:
    def __init__(self, parent_frame, db_connection, app=None):
        self.results_table = None
        self.date_to_entry = None
        self.date_from_entry = None
        self.room_combobox = None
        self.client_combobox = None
        self.parent_frame = parent_frame
        self.db_connection = db_connection
        self.app = app
        self.create_filter_form()
        self.refresh_data()
    
    def refresh_data(self):
        """Обновление данных клиентов и номеров"""
        self.clients = self.fetch_clients_for_import()
        self.rooms = self.fetch_rooms_for_import()
        
        if hasattr(self, 'client_combobox'):
            self.load_clients()
        
        if hasattr(self, 'room_combobox'):
            self.load_rooms()
        
        # Обновляем таблицу результатов
        self.reload_all_bookings()
    
    def fetch_clients_for_import(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_CLIENTS_FOR_BOOKINGS_SQL)
        data = cur.fetchall()
        cur.close()
        return data
    
    def fetch_rooms_for_import(self):
        cur = self.db_connection.cursor()
        cur.execute(FETCH_ROOMS_FOR_BOOKINGS_SQL)
        data = cur.fetchall()
        cur.close()
        return data
    
    def create_filter_form(self):
        # Фильтр по клиенту
        ttk.Label(self.parent_frame, text='Фильтр по клиенту').grid(row=0, column=0, padx=(10, 5), pady=5, sticky='e')
        self.client_combobox = ttk.Combobox(self.parent_frame, state="readonly")
        self.client_combobox.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='w')
        
        # Фильтр по номеру
        ttk.Label(self.parent_frame, text='Фильтр по номеру').grid(row=1, column=0, padx=(10, 5), pady=5, sticky='e')
        self.room_combobox = ttk.Combobox(self.parent_frame, state="readonly")
        self.room_combobox.grid(row=1, column=1, padx=(5, 10), pady=5, sticky='w')
        
        # Фрейм для фильтров по дате
        date_frame = ttk.Frame(self.parent_frame)
        date_frame.grid(row=2, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        ttk.Label(date_frame, text='Дата заселения от').grid(row=0, column=0, padx=(10, 5), pady=5, sticky='e')
        self.date_from_entry = DateEntry(date_frame, date_pattern='y-mm-dd', locale='ru_RU')
        self.date_from_entry.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='w')
        self.date_from_entry.delete(0, 'end')
        
        ttk.Label(date_frame, text='до').grid(row=0, column=2, padx=(10, 5), pady=5, sticky='e')
        self.date_to_entry = DateEntry(date_frame, date_pattern='y-mm-dd', locale='ru_RU')
        self.date_to_entry.grid(row=0, column=3, padx=(5, 10), pady=5, sticky='w')
        self.date_to_entry.delete(0, 'end')
        
        # Таблица результатов
        self.results_table = ttk.Treeview(self.parent_frame, columns=(
            'ID', 'Клиент', 'Номер', 'Дата заселения', 'Дата выселения', 'Примечание'),
            show='headings')
        for label in self.results_table["columns"]:
            self.results_table.heading(label, text=label)
        self.results_table.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.results_table.yview)
        self.results_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=2, sticky='ns')
        
        # Фрейм для кнопок
        buttons_frame = ttk.Frame(self.parent_frame)
        buttons_frame.grid(row=4, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        buttons_frame.columnconfigure(3, weight=1)
        
        ttk.Button(buttons_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(buttons_frame, text="Очистить", command=self.clear_filters).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        word_button = ttk.Button(buttons_frame, text="Экспорт в Word", command=self.export_to_word)
        word_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        excel_button = ttk.Button(buttons_frame, text="Экспорт в Excel", command=self.export_to_excel)
        excel_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        excel_imp_button = ttk.Button(buttons_frame, text="Импорт из Excel", command=self.handle_import_excel)
        excel_imp_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        
        word_imp_button = ttk.Button(buttons_frame, text="Импорт из Word", command=self.handle_import_word)
        word_imp_button.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        refresh_button = ttk.Button(buttons_frame, text="Обновить данные", command=self.refresh_data)
        refresh_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        max_button_width = max(word_button.winfo_reqwidth(), excel_button.winfo_reqwidth(), 
                              word_imp_button.winfo_reqwidth(), excel_imp_button.winfo_reqwidth())
        word_button.config(width=max_button_width)
        excel_button.config(width=max_button_width)
        word_imp_button.config(width=max_button_width)
        excel_imp_button.config(width=max_button_width)
    
    def handle_import_excel(self):
        def on_data(headers, rows):
            self.process_imported_data(headers, rows)
        import_from_excel(self.parent_frame.winfo_toplevel(), on_data)
    
    def handle_import_word(self):
        def on_data(headers, rows):
            self.process_imported_data(headers, rows)
        import_from_word(self.parent_frame.winfo_toplevel(), on_data)
    
    def process_imported_data(self, headers, rows):
        try:
            imported_count = 0
            for row in rows:
                if len(row) < 5:
                    continue
                
                client_name = row[0] if len(row) > 0 else ""
                room_info = row[1] if len(row) > 1 else ""
                check_in_date = row[2] if len(row) > 2 else ""
                check_out_date = row[3] if len(row) > 3 else ""
                note = row[4] if len(row) > 4 else ""
                
                # Пропускаем строки с недостаточными данными
                if not client_name or not room_info or not check_in_date:
                    continue
                
                client_id = next((client[0] for client in self.clients if f"{client[1]} {client[2]} {client[3]}" == client_name), None)
                room_id = next((room[0] for room in self.rooms if f"{room[1]} ({room[2]})" == room_info), None)
                
                if not client_id or not room_id:
                    continue
                
                cur = self.db_connection.cursor()
                cur.execute(INSERT_BOOKING_SQL, (client_id, room_id, check_in_date, check_out_date, note))
                self.db_connection.commit()
                cur.close()
                imported_count += 1
            
            self.reload_all_bookings()
            
            # Обновляем данные в других модулях
            if self.app and hasattr(self.app, 'bookings'):
                self.app.bookings.show_bookings()
            
            messagebox.showinfo("Успех", f"Данные успешно импортированы! Добавлено {imported_count} записей.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")
    
    def reload_all_bookings(self):
        cur = self.db_connection.cursor()
        cur.execute("""
            SELECT b.booking_id, 
                   c.last_name || ' ' || c.first_name || ' ' || c.middle_name AS client_name,
                   r.room_number || ' (' || r.comfort_level || ')' AS room_info,
                   b.check_in_date, b.check_out_date, b.note
            FROM bookings b
            JOIN clients c ON b.client_id = c.client_id
            JOIN rooms r ON b.room_id = r.room_id
            ORDER BY b.check_in_date DESC
        """)
        results = cur.fetchall()
        cur.close()
        
        for row in self.results_table.get_children():
            self.results_table.delete(row)
        for result in results:
            self.results_table.insert('', 'end', values=result)
    
    def export_to_word(self):
        export_to_word(self)
    
    def export_to_excel(self):
        export_to_excel(self)
    
    def clear_filters(self):
        self.client_combobox.set('')
        self.room_combobox.set('')
        self.date_from_entry.delete(0, 'end')
        self.date_to_entry.delete(0, 'end')
        self.reload_all_bookings()
    
    def load_clients(self):
        cur = self.db_connection.cursor()
        cur.execute(LOAD_CLIENTS_FOR_FILTER_SQL)
        clients = cur.fetchall()
        cur.close()
        self.client_combobox['values'] = [f"{client[1]} {client[2]} {client[3]}" for client in clients]
    
    def load_rooms(self):
        cur = self.db_connection.cursor()
        cur.execute(LOAD_ROOMS_FOR_FILTER_SQL)
        rooms = cur.fetchall()
        cur.close()
        self.room_combobox['values'] = [f"{room[1]} ({room[2]})" for room in rooms]
    
    def apply_filter(self):
        client_name = self.client_combobox.get()
        room_info = self.room_combobox.get()
        
        client_id = None
        room_id = None
        
        if client_name:
            cur = self.db_connection.cursor()
            cur.execute(CLIENT_FILTER_SQL, (client_name,))
            result = cur.fetchone()
            if result:
                client_id = result[0]
            cur.close()
        
        if room_info:
            room_number = room_info.split(' ')[0]
            cur = self.db_connection.cursor()
            cur.execute(ROOM_FILTER_SQL, (room_number,))
            result = cur.fetchone()
            if result:
                room_id = result[0]
            cur.close()
        
        date_from = self.date_from_entry.get() if self.date_from_entry.get() else None
        date_to = self.date_to_entry.get() if self.date_to_entry.get() else None
        
        try:
            cur = self.db_connection.cursor()
            cur.execute(
                APPLY_FILTERS_SQL, (client_id, client_id, room_id, room_id, date_from, date_from, date_to, date_to)
            )
            results = cur.fetchall()
            cur.close()
            
            for row in self.results_table.get_children():
                self.results_table.delete(row)
            for result in results:
                self.results_table.insert('', 'end', values=result)
                
            messagebox.showinfo("Успех", f"Найдено {len(results)} записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр: {e}")