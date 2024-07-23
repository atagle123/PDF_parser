import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import filedialog
from table_extractor.extractor import PDF_num_table




class PDFTableExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Table Extractor")

        #self.root.geometry('290x162')

        self.create_widgets()

    def create_widgets(self):
        # Create a label
        label = tk.Label(self.root, text="Welcome to the PDF Table Extractor")
        label.pack(pady=10)
        
        # Create labels and entry fields for start and end pages
        self.start_page_label = tk.Label(self.root, text="Pages:")
        self.start_page_label.pack(pady=5)
        self.start_page_entry = tk.Entry(self.root)
        self.start_page_entry.pack(pady=5)
        
        self.pdf_type = tk.Label(root, text="flavor:")
        self.pdf_type.pack(pady=5)
        self.pdf_type_entry = tk.Entry(root)
        self.pdf_type_entry.pack(pady=5)

        self.row_tol = tk.Label(root, text="row_tol:")
        self.row_tol.pack(pady=5)
        self.row_tol_entry = tk.Entry(root)
        self.row_tol_entry.pack(pady=5)

        self.edge_tol = tk.Label(root, text="edge_tol:")
        self.edge_tol.pack(pady=5)
        self.edge_tol_entry = tk.Entry(root)
        self.edge_tol_entry.pack(pady=5)

        self.column_tol = tk.Label(root, text="column_tol:")
        self.column_tol.pack(pady=5)
        self.column_tol_entry = tk.Entry(root)
        self.column_tol_entry.pack(pady=5)
        
        # Create an open file button
        self.open_button = tk.Button(self.root, text="Open PDF", command=self.open_file)
        self.open_button.pack(pady=5)

        self.extract = tk.Button(self.root, text="Extract PDF", command=self.main)
        self.extract.pack(pady=5)
        self.extract.config(state="disabled")
        
        # Create an exit button
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=5)
    
    def get_entries(self):
        """Get values from input fields and return them in a dictionary with defaults."""

        self.kwargs  = {
            'pages': str(self.start_page_entry.get()) or "all",
            "flavor": str(self.pdf_type_entry.get()) or "stream",
            "row_tol": int(self.row_tol_entry.get() or 5) ,
            "edge_tol": int(self.edge_tol_entry.get() or 10000),
            "column_tol": int(self.column_tol_entry.get() or 0)
        }


    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_path=file_path
            self.extract.config(state="normal")
    
    def save_file(self):
        directory_path = filedialog.askdirectory(
            title="Seleccionar directorio de guardado"  # Título de la ventana de diálogo
        )

        if directory_path:
            self.save_path=directory_path


    def main(self):
        self.get_entries()
        if self.file_path:
            pdf_instance=PDF_num_table(self.file_path)

            pdf_instance.extract_tables(**self.kwargs)
            pdf_instance.main_preprocessing_tables()
            
            self.save_file()

            if self.save_path:
                pdf_instance.excel_path=self.save_path
            filename=self.make_filename()
            pdf_instance.save_tables_to_excel(filename=filename)
        else:
            raise FileNotFoundError

    def make_filename(self):
        filename=os.path.basename(self.file_path)
        pages=self.kwargs["pages"]
        return(f"pdf_tables_{filename}_{pages}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTableExtractorApp(root)
    root.mainloop()
