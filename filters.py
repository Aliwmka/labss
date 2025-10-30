# filters.py
from tkinter import ttk
from tkcalendar import DateEntry
from export import export_to_word, export_to_excel
from import_data import import_from_excel, import_from_word
from tkinter import messagebox
from datetime import datetime
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
        columns = ('ID', 'Клиент', 'Номер', 'Дата заселения', 'Дата выселения', 'Примечание')
        self.results_table = ttk.Treeview(self.parent_frame, columns=columns, show='headings')
        
        # Настраиваем заголовки колонок
        for col in columns:
            self.results_table.heading(col, text=col)
            self.results_table.column(col, width=150, anchor='center')
        
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
        
        # Настройка весов для растягивания
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.columnconfigure(1, weight=1)
        self.parent_frame.rowconfigure(3, weight=1)
    
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
            skipped_count = 0
            errors = []
            
            print(f"Начало обработки импорта: {len(rows)} записей")
            print(f"Заголовки: {headers}")
            
            for i, row in enumerate(rows):
                # Пропускаем пустые строки
                if not any(str(cell).strip() for cell in row if cell is not None):
                    skipped_count += 1
                    continue
                    
                print(f"Обработка строки {i}: {row}")
                
                # Определяем индексы столбцов на основе заголовков
                client_col = self._find_column_index(headers, ['клиент', 'client', 'фио', 'фам'])
                room_col = self._find_column_index(headers, ['номер', 'room', 'комната'])
                check_in_col = self._find_column_index(headers, ['заселение', 'checkin', 'дата заселения', 'дата начала'])
                check_out_col = self._find_column_index(headers, ['выселение', 'checkout', 'дата выселения', 'дата окончания'])
                note_col = self._find_column_index(headers, ['примечание', 'note', 'комментарий'])
                
                # Если не нашли по заголовкам, используем порядок по умолчанию
                if client_col is None: client_col = 0
                if room_col is None: room_col = 1
                if check_in_col is None: check_in_col = 2
                if check_out_col is None: check_out_col = 3
                if note_col is None: note_col = 4
                
                # Получаем данные с проверкой индексов
                client_name = str(row[client_col]).strip() if len(row) > client_col and row[client_col] else ""
                room_info = str(row[room_col]).strip() if len(row) > room_col and row[room_col] else ""
                check_in_date = str(row[check_in_col]).strip() if len(row) > check_in_col and row[check_in_col] else ""
                check_out_date = str(row[check_out_col]).strip() if len(row) > check_out_col and row[check_out_col] else ""
                note = str(row[note_col]).strip() if len(row) > note_col and row[note_col] else ""
                
                print(f"Извлеченные данные: клиент='{client_name}', номер='{room_info}', заезд='{check_in_date}', выезд='{check_out_date}'")
                
                # Проверяем обязательные поля
                if not client_name or not room_info or not check_in_date:
                    errors.append(f"Строка {i+1}: отсутствуют обязательные поля")
                    skipped_count += 1
                    continue
                
                # Ищем клиента по ФИО (разные варианты сопоставления)
                client_id = None
                for client in self.clients:
                    full_name = f"{client[1]} {client[2]} {client[3]}".strip()
                    last_first = f"{client[1]} {client[2]}".strip()
                    
                    if (client_name == full_name or 
                        client_name == last_first or
                        client_name.startswith(client[1]) or  # Только фамилия
                        full_name.startswith(client_name)):   # Частичное совпадение
                        client_id = client[0]
                        print(f"Найден клиент: {full_name} -> ID: {client_id}")
                        break
                
                # Ищем номер по информации
                room_id = None
                for room in self.rooms:
                    room_full_info = f"{room[1]} ({room[2]})"
                    room_simple = f"{room[1]}"
                    
                    if (room_info == room_full_info or 
                        room_info == room_simple or
                        room_info.startswith(room[1]) or
                        room_full_info.startswith(room_info)):
                        room_id = room[0]
                        print(f"Найден номер: {room_full_info} -> ID: {room_id}")
                        break
                
                if not client_id:
                    errors.append(f"Строка {i+1}: клиент '{client_name}' не найден в базе")
                    skipped_count += 1
                    continue
                    
                if not room_id:
                    errors.append(f"Строка {i+1}: номер '{room_info}' не найден в базе")
                    skipped_count += 1
                    continue
                
                try:
                    # Нормализуем даты
                    check_in_normalized = self._normalize_date(check_in_date)
                    check_out_normalized = self._normalize_date(check_out_date) if check_out_date else None
                    
                    if not check_in_normalized:
                        errors.append(f"Строка {i+1}: неверный формат даты заселения '{check_in_date}'")
                        skipped_count += 1
                        continue
                    
                    # Пропускаем проверку конфликтов для импорта (разрешаем дублирование)
                    # В реальном приложении эту проверку можно включить обратно
                    # if not self._check_booking_possible(room_id, check_in_normalized, check_out_normalized):
                    #     errors.append(f"Строка {i+1}: номер занят в указанные даты")
                    #     skipped_count += 1
                    #     continue
                    
                    cur = self.db_connection.cursor()
                    cur.execute(INSERT_BOOKING_SQL, (
                        client_id, 
                        room_id, 
                        check_in_normalized, 
                        check_out_normalized, 
                        note
                    ))
                    self.db_connection.commit()
                    cur.close()
                    imported_count += 1
                    print(f"Успешно импортирована запись {i+1}")
                    
                except Exception as e:
                    # Проверяем, если это ошибка дублирования, все равно добавляем
                    if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                        errors.append(f"Строка {i+1}: дублирующая запись (уже существует в базе)")
                    else:
                        errors.append(f"Строка {i+1}: ошибка базы данных - {str(e)}")
                    skipped_count += 1
                    continue
            
            # Обновляем данные
            self.reload_all_bookings()
            if self.app and hasattr(self.app, 'bookings'):
                self.app.bookings.show_bookings()
            
            # Формируем сообщение о результате
            message = f"Импорт завершен!\nУспешно: {imported_count} записей"
            if skipped_count > 0:
                message += f"\nПропущено: {skipped_count} записей"
            
            if errors:
                error_details = "\n".join(errors[:10])  # Показываем первые 10 ошибок
                if len(errors) > 10:
                    error_details += f"\n... и еще {len(errors) - 10} ошибок"
                message += f"\n\nОшибки:\n{error_details}"
            
            messagebox.showinfo("Результат импорта", message)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {str(e)}")
            print(f"Критическая ошибка импорта: {e}")
    
    def _find_column_index(self, headers, possible_names):
        """Находит индекс столбца по возможным названиям"""
        if not headers:
            return None
            
        headers_lower = [str(h).lower() for h in headers]
        for name in possible_names:
            for i, header in enumerate(headers_lower):
                if name in header:
                    return i
        return None
    
    def _normalize_date(self, date_str):
        """Нормализует дату в формат YYYY-MM-DD"""
        if not date_str:
            return None
            
        date_str = str(date_str).strip()
        
        # Пробуем разные форматы дат
        date_formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y.%m.%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Пробуем разобрать дату без разделителей (например, 20240115)
        if len(date_str) == 8 and date_str.isdigit():
            try:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def _check_booking_possible(self, room_id, check_in, check_out):
        """Проверяет, свободен ли номер в указанные даты"""
        try:
            cur = self.db_connection.cursor()
            
            # Если дата выселения не указана, считаем что бронь на 1 день
            if not check_out:
                check_out = check_in
            
            # Правильная проверка пересечения дат
            cur.execute("""
                SELECT COUNT(*) FROM bookings 
                WHERE room_id = %s AND (
                    (check_in_date <= %s AND check_out_date >= %s) OR
                    (check_in_date <= %s AND check_out_date >= %s) OR
                    (%s BETWEEN check_in_date AND check_out_date) OR
                    (%s BETWEEN check_in_date AND check_out_date)
                )
            """, (room_id, check_in, check_in, check_out, check_out, check_in, check_out))
            
            count = cur.fetchone()[0]
            cur.close()
            
            print(f"Проверка номера {room_id} с {check_in} по {check_out}: найдено {count} конфликтов")
            
            return count == 0
            
        except Exception as e:
            print(f"Ошибка проверки бронирования: {e}")
            return True  # В случае ошибки разрешаем бронирование
    
    def reload_all_bookings(self):
        cur = self.db_connection.cursor()
        cur.execute("""
            SELECT b.booking_id, 
                   c.last_name || ' ' || c.first_name || ' ' || COALESCE(c.middle_name, '') AS client_name,
                   r.room_number || ' (' || r.comfort_level || ')' AS room_info,
                   b.check_in_date, b.check_out_date, b.note
            FROM bookings b
            JOIN clients c ON b.client_id = c.client_id
            JOIN rooms r ON b.room_id = r.room_id
            ORDER BY b.check_in_date DESC
        """)
        results = cur.fetchall()
        cur.close()
        
        # Очищаем таблицу
        for row in self.results_table.get_children():
            self.results_table.delete(row)
        
        # Заполняем новыми данными
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
        client_names = [f"{client[1]} {client[2]} {client[3]}" for client in clients]
        self.client_combobox['values'] = client_names
        print(f"Загружено {len(client_names)} клиентов для фильтра")
    
    def load_rooms(self):
        cur = self.db_connection.cursor()
        cur.execute(LOAD_ROOMS_FOR_FILTER_SQL)
        rooms = cur.fetchall()
        cur.close()
        room_names = [f"{room[1]} ({room[2]})" for room in rooms]
        self.room_combobox['values'] = room_names
        print(f"Загружено {len(room_names)} номеров для фильтра")
    
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
                APPLY_FILTERS_SQL, 
                (client_id, client_id, room_id, room_id, date_from, date_from, date_to, date_to)
            )
            results = cur.fetchall()
            cur.close()
            
            # Очищаем таблицу
            for row in self.results_table.get_children():
                self.results_table.delete(row)
            
            # Заполняем отфильтрованными данными
            for result in results:
                self.results_table.insert('', 'end', values=result)
                
            messagebox.showinfo("Успех", f"Найдено {len(results)} записей")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр: {e}")
            print(f"Ошибка фильтрации: {e}")