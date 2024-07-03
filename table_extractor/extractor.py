import camelot
import fitz  # PyMuPDF
from thefuzz import fuzz
import datetime
import re
from pdfquery import PDFQuery


def extract_titles_and_tables(pdf_file):
    tables_with_titles = []

    # Extract tables from each page using Camelot
    tables = camelot.read_pdf(pdf_file,flavor='stream',pages="all",row_tol=10, strip_text='\n',edge_tol=500,column_tol=5)

    # Open the PDF document with PyMuPDF
    doc = fitz.open(pdf_file)
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',                    # 01/31/2023
        r'\d{1,2}-\d{1,2}-\d{4}',                    # 01-31-2023
        r'\d{4}-\d{2}-\d{2}',                        # 2023-01-31
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # 31 Jan 2023
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',  # Jan 31, 2023
    ]

    # Compile regex patterns
    regex = re.compile('|'.join(date_patterns))

    for table in tables:
        # Extract text from the page for title extraction
        page_num = table.page - 1  # Page numbers in Camelot are 1-based

        """  # Load the page using PyMuPDF
        page = doc.load_page(page_num)

        # Extracting text from the current page
        text = page.get_text(sort=True,flags=2) #option="blocks"(option="blocks",flags=2)
    
        # Close the document
        matches = regex.findall(text)
        date_results = []

        for match in matches:
            try:
                # Validate the matched date using datetime.strptime
               # date_obj = datetime.strptime(match, '%m/%d/%Y')  # Adjust format string as needed
                date_results.append((page_num + 1, match))  # Store page number and date string
            except ValueError:
                continue  # Skip if date format does not match"""
    

        # Extract title for the current table
        title = extract_title_above_table(page_num, table)
        tables_with_titles.append((title, table.df))
    doc.close()
    return tables_with_titles


def extract_title_above_table(page_num, table):
    top_ypos_table=table.rows[0][0]
    x_pos_table_min=table.cols[0][0]
    x_pos_table_max=table.cols[-1][-1]

    pdf = PDFQuery(pdf_file)
    pdf.load(page_num)


    # Use CSS-like selectors to locate the elements
    for i in range(100):
        text_elements = pdf.pq('LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")' % (x_pos_table_min, top_ypos_table, x_pos_table_max, top_ypos_table+i)).text()
        if len(text_elements)!=0 :
            break
    
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',                    # 01/31/2023
        r'\d{1,2}-\d{1,2}-\d{4}',                    # 01-31-2023
        r'\d{4}-\d{2}-\d{2}',                        # 2023-01-31
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # 31 Jan 2023
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',  # Jan 31, 2023
    ]

    # Compile regex patterns
    regex = re.compile('|'.join(date_patterns))
    matches = regex.findall(text_elements)
    date_results = []
    print(matches)
    for match in matches:
        try:
            # Validate the matched date using datetime.strptime
            # date_obj = datetime.strptime(match, '%m/%d/%Y')  # Adjust format string as needed
            date_results.append((page_num + 1, match))  # Store page number and date string
        except ValueError:
            continue  # Skip if date format does not match"""


    return(text_elements)






def extract_text_chunks(filename):
    doc = fitz.open(filename)
    chunks = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block["type"] == 0:  # Text block
                chunks.append(block["lines"][0]["spans"][0]["text"])
    
    return chunks






# Example usage:
pdf_file = "Estados_financieros_2010_03-páginas.pdf"
list=tables_with_titles = extract_titles_and_tables(pdf_file)

#from tabula import read_pdf
from camelot import read_pdf
import pandas as pd
import os

class BasePDFclass:
    def __init__(self,pdf_path):
        self.pdf_path = pdf_path
    
    def extract_tables(self):
        """ Método a implementar que entregue todas las tablas en formato de una ista de dataframes
        """
        raise NotImplementedError

class Image_PDF_extractor():
    def __init__(self):
        pass

    def exctract_tables(self):
        pass



class Text_PDF_extractor():
    def __init__(self):
        pass
    def extract_tables(self,pdf_path,pages="all"):
        df = read_pdf(pdf_path,pages=pages)
        return(df)


class PDF_tables(BasePDFclass):
    """Class that exctract all the tables of the pdf"""
    
    def __init__(self, pdf_path):
        super().__init__(pdf_path)
        self.text_extractor=Text_PDF_extractor()
        self.image_exctractor=Image_PDF_extractor()

        current_dir = os.getcwd()
        self.csv_path=os.path.join(current_dir, "data","industrydata","pdf","csv")
        self.excel_path=os.path.join(current_dir, "data", "industrydata", "pdf", "excel")

        os.makedirs(self.excel_path, exist_ok=True)
        os.makedirs(self.csv_path, exist_ok=True)



    def extract_tables(self,pages="all"):
        #df_images=self.image_exctractor.extract_tables(pages=pages)
        df_text=self.text_extractor.extract_tables(self.pdf_path,pages=pages)
        #hacer un merge de las dos listas...
        # ojo que en el merge es probable que se repitan las dos tablas
        self.df_list=df_text
        print(f"Extracted {len(self.df_list)} tables")

    def search_concept(self,concept=None): # quizas hacer uno de si es el titulo o no...
        """ Search for a concept in the dataframes, if given, returns a list of dataframes with the given concept
            quizas pasar todo a minuscula...  o a regex
        """ 
        if concept==None:
            return(self.df_list)
        
        match_list=[]
        for df in self.df_list:

            df_lower = df.map(lambda x: x.lower() if isinstance(x, str) else x) # uses lower case to match

            is_string_present = df_lower.isin([concept]).any().any()
            if is_string_present:
                match_list.append(df)
        return(match_list)
    
    def preprocess_data(self,df_list,function=None):
        "quizas implementar funciones propias por empresa..."

        for i,df in enumerate(df_list):

            df = df.apply(lambda x: x.astype(str).str.replace('.', ''))
            df = df.apply(lambda x: x.astype(str).str.replace('(', ''))
            df = df.apply(lambda x: x.astype(str).str.replace(')', ''))
            df = df.apply(lambda x: x.astype(str).str.replace('_', ''))
            df = df.apply(lambda x: x.astype(str).str.replace('-', ''))
            df.dropna(how="all",inplace=True)
            df = df.map(lambda x: x.lower() if isinstance(x, str) else x)
            df_list[i]=df

        return(df_list)
    
    def tables_to_excel(self,filename,concept=None):
        
        match_list=self.search_concept(concept)
        df_preprocess_list=self.preprocess_data(match_list)
        print(len(df_preprocess_list))
        filepath=os.path.join(self.excel_path, f"{filename}.xlsx")

        with pd.ExcelWriter(filepath) as writer:
            for  i,df in enumerate(df_preprocess_list):
                df.to_excel(writer,sheet_name=f"sheetname_{i}")
        pass
    
    def download_table(self,path,table_name): # ver como seleccionar una tabla para descargar... 
        raise NotImplementedError
