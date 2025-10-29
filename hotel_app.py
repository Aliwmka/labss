import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from db_connection import get_sync_db_connection
from clients import Clients
from rooms import Rooms
from bookings import Bookings
from filters import DataFilter

class HotelApp(tk.Tk):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        
        self.clients_frame = None
        self.rooms_frame = None
        self.bookings_frame = None
        self.filter_frame = None
        
        self.clients = None
        self.rooms = None
        self.bookings = None
        self.data_filter = None
        
        self.title("Гостиница - система управления")
        self.geometry("1700x600")
        
        # Настройка шрифта по умолчанию должна быть ПОСЛЕ создания главного окна
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        # Настройка цветов и шрифтов
        self.style.configure('TFrame', background='#fff0f5')
        self.style.configure('TLabel', background='#fff0f5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), foreground='black', background='#ffb6c1')
        self.style.map('TButton',
                      foreground=[('active', 'black'), ('pressed', 'white')],
                      background=[('active', '#ff91a4'), ('pressed', '#8b475d')])
        
        self.style.configure('Treeview',
                            rowheight=25,
                            font=('Arial', 9),
                            background='#ffffff',
                            fieldbackground='#ffffff')
        self.style.configure('Treeview.Heading',
                            font=('Arial', 10, 'bold'),
                            background='#ffe4e1')
        
        # Цвет основного окна
        self.configure(bg='#fff0f5')
        
        self.create_widgets()
        self.show()
    
    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        
        # Клиенты
        self.clients_frame = ttk.Frame(tab_control)
        tab_control.add(self.clients_frame, text='Клиенты')
        self.clients = Clients(self.clients_frame, self.db_connection)
        
        # Номера
        self.rooms_frame = ttk.Frame(tab_control)
        tab_control.add(self.rooms_frame, text='Номера')
        self.rooms = Rooms(self.rooms_frame, self.db_connection)
        
        # Бронирования
        self.bookings_frame = ttk.Frame(tab_control)
        tab_control.add(self.bookings_frame, text='Бронирования')
        self.bookings = Bookings(self.bookings_frame, self.db_connection)
        
        # Фильтрация данных
        self.filter_frame = ttk.Frame(tab_control)
        tab_control.add(self.filter_frame, text='Фильтрация данных')
        self.data_filter = DataFilter(self.filter_frame, self.db_connection)
        
        tab_control.pack(expand=1, fill='both')
    
    def show(self):
        self.clients.show_clients()
        self.rooms.show_rooms()
        self.bookings.show_bookings()

def main():
    conn = None
    try:
        conn = get_sync_db_connection()
        app = HotelApp(conn)
        app.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()