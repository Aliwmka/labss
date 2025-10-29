from docx import Document
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def import_from_excel(parent_window, callback):
    filepath = filedialog.askopenfilename(
        parent=parent_window,
        title="Выберите файл Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not filepath:
        return

    try:
        df = pd.read_excel(filepath, dtype=str)
        data = df.values.tolist()
        headers = df.columns.tolist()
        callback(headers, data)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать Excel: {e}")

def import_from_word(parent_window, callback):
    filepath = filedialog.askopenfilename(
        parent=parent_window,
        title="Выберите файл Word",
        filetypes=[("Word files", "*.docx")]
    )
    if not filepath:
        return

    try:
        doc = Document(filepath)
        if not doc.tables:
            messagebox.showwarning("Внимание", "В документе нет таблиц.")
            return

        table = doc.tables[0]
        data = []
        headers = None
        for i, row in enumerate(table.rows):
            row_data = [cell.text.strip() for cell in row.cells]
            if i == 0:
                headers = row_data
            else:
                data.append(row_data)
        callback(headers, data)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать Word: {e}")