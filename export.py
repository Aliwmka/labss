# export.py
from docx import Document
import pandas as pd
import os
from datetime import datetime

def export_to_word(self):
    try:
        rows = [(self.results_table.item(item)["values"]) for item in self.results_table.get_children()]
        
        if not rows:
            from tkinter import messagebox
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        doc = Document()
        doc.add_heading('Отчет по бронированиям гостиницы', 0)
        
        table = doc.add_table(rows=1, cols=len(self.results_table["columns"]))
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(self.results_table["columns"]):
            hdr_cells[i].text = column
        
        for row in rows:
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value) if value is not None else ""
        
        client_option = self.client_combobox.get() or "все"
        room_option = self.room_combobox.get() or "все"
        date_from_option = self.date_from_entry.get() or "все"
        date_to_option = self.date_to_entry.get() or "все"
        
        # Создаем папку для отчетов, если ее нет
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/Отчет_бронирования_{client_option}_{room_option}_{date_from_option}_{date_to_option}_{timestamp}.docx".replace(' ', '_')
        doc.save(filename)
        
        from tkinter import messagebox
        messagebox.showinfo("Успех", f"Отчет сохранен в {filename}")
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Ошибка", f"Не удалось экспортировать в Word: {e}")

def export_to_excel(self):
    try:
        rows = [(self.results_table.item(item)["values"]) for item in self.results_table.get_children()]
        
        if not rows:
            from tkinter import messagebox
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        columns = self.results_table["columns"]
        
        df = pd.DataFrame(rows, columns=columns)
        client_option = self.client_combobox.get() or "все"
        room_option = self.room_combobox.get() or "все"
        date_from_option = self.date_from_entry.get() or "все"
        date_to_option = self.date_to_entry.get() or "все"
        
        # Создаем папку для отчетов, если ее нет
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/Отчет_бронирования_{client_option}_{room_option}_{date_from_option}_{date_to_option}_{timestamp}.xlsx".replace(' ', '_')
        df.to_excel(filename, index=False)
        
        from tkinter import messagebox
        messagebox.showinfo("Успех", f"Отчет сохранен в {filename}")
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Ошибка", f"Не удалось экспортировать в Excel: {e}")