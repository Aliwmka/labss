from docx import Document
import pandas as pd

def export_to_word(self):
    rows = [(self.results_table.item(item)["values"]) for item in self.results_table.get_children()]
    
    doc = Document()
    doc.add_heading('Отчет по бронированиям гостиницы', 0)
    
    table = doc.add_table(rows=1, cols=len(self.results_table["columns"]))
    hdr_cells = table.rows[0].cells
    for i, column in enumerate(self.results_table["columns"]):
        hdr_cells[i].text = column
    
    for row in rows:
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)
    
    client_option = self.client_combobox.get() or "все"
    room_option = self.room_combobox.get() or "все"
    date_from_option = self.date_from_entry.get() or "все"
    date_to_option = self.date_to_entry.get() or "все"
    
    filename = f"Отчет_бронирования_{client_option}_{room_option}_{date_from_option}_{date_to_option}.docx".replace(' ', '_')
    doc.save(filename)
    print(f"Отчет сохранен в {filename}")

def export_to_excel(self):
    rows = [(self.results_table.item(item)["values"]) for item in self.results_table.get_children()]
    columns = self.results_table["columns"]
    
    df = pd.DataFrame(rows, columns=columns)
    client_option = self.client_combobox.get() or "все"
    room_option = self.room_combobox.get() or "все"
    date_from_option = self.date_from_entry.get() or "все"
    date_to_option = self.date_to_entry.get() or "все"
    
    filename = f"Отчет_бронирования_{client_option}_{room_option}_{date_from_option}_{date_to_option}.xlsx".replace(' ', '_')
    df.to_excel(filename, index=False)
    print(f"Отчет сохранен в {filename}")