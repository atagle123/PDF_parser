import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import filedialog, messagebox
from table_extractor.extractor import PDF_num_table

import tkinter as tk
from tkinter import filedialog, messagebox



class PDFTableExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Table Extractor")
        self.create_widgets()

    def create_widgets(self):
        # Create a label
        label = tk.Label(self.root, text="Welcome to the PDF Table Extractor")
        label.pack(pady=10)
        
        # Create labels and entry fields for start and end pages
        self.start_page_label = tk.Label(self.root, text="Start Page:")
        self.start_page_label.pack(pady=5)
        self.start_page_entry = tk.Entry(self.root)
        self.start_page_entry.pack(pady=5)
        
        self.end_page_label = tk.Label(self.root, text="End Page:")
        self.end_page_label.pack(pady=5)
        self.end_page_entry = tk.Entry(self.root)
        self.end_page_entry.pack(pady=5)

        pdf_type = tk.Label(root, text="PDF type:")
        pdf_type.pack(pady=5)
        pdf_type = tk.Entry(root)
        pdf_type.pack(pady=5)
        
        # Create an open file button
        self.open_button = tk.Button(self.root, text="Open PDF", command=self.open_file)
        self.open_button.pack(pady=5)
        
        # Create an exit button
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=5)
    
    def get_entries(self):
        """Get values from input fields and return them in a dictionary with defaults."""
        print(str(self.end_page_entry.get()))
        values = {
            'start_page': str(self.start_page_entry.get()) if self.start_page_entry.get().isdigit() else 1,
            'end_page': str(self.end_page_entry.get()) if self.end_page_entry.get().isdigit() else float('inf')
        }
        return values
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_path=file_path
    
    def save_file(self, tables):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if save_path:
            try:
                with open(save_path, "w") as f:
                    for table in tables:
                        for row in table:
                            f.write("\t".join(str(cell) for cell in row) + "\n")
                        f.write("\n")
                messagebox.showinfo("Success", "Tables extracted and saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTableExtractorApp(root)
    root.mainloop()
