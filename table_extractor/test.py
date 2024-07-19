import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from table_extractor.extractor import PDF_num_table


def main(pdf_path,pages):
    pdf_instance=PDF_num_table(pdf_path)
    tables=pdf_instance.extract_tables(pages=pages) # usar variables: path, pages, stream ,flavor='stream',row_tol=5, strip_text='\n',edge_tol=10000,column_tol=0) y variable separador
    new_tables=pdf_instance.main_preprocessing_tables()
    pdf_instance.save_tables_to_excel(filename="excel_test")






if __name__=="__main__":
    pdf_path="Estados_financieros_2010_03-páginas.pdf"
    pdf_path="IFS 1Q24.pdf"
    pages="3"

    main(pdf_path=pdf_path)