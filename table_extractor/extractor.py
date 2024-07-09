import camelot
import fitz  # PyMuPDF
from thefuzz import fuzz
import datetime
import re
from pdfquery import PDFQuery
#from tabula import read_pdf
from camelot import read_pdf
import pandas as pd
import os


class Image_PDF_extractor:
    def __init__(self):
        pass

    def exctract_tables(self):
        raise NotImplementedError



class Text_PDF_extractor:
    def __init__(self,pdf_path,save_path): # implement save path 
        self.pdf_path=pdf_path
        current_dir = os.getcwd()
        self.csv_path=os.path.join(current_dir, "data","csv")
        self.excel_path=os.path.join(current_dir, "data","excel")
        pass

    def extract_tables(self,pdf_path,pages="all"):
        table_list = read_pdf(pdf_path,pages=pages) #,flavor='stream',pages="all",row_tol=5, strip_text='\n',edge_tol=10000,column_tol=0)#,layout_kwargs={"boxes_flow":1})
        self.table_list=table_list._tables # list of camelot tables object to acces a table is table_list[number].df
        print(f"Extracted {len(table_list._tables)} tables")

        return(self.table_list)
    

    def visualize_tables(self,table_num):
        return(camelot.plot(self.table_list[table_num], kind='contour').show()) #write others kind of visualizations

    def filter_by_accuracy(self,acc=88):#'accuracy': 99.99999999999999, acc bewtween 0 and 100#'whitespace': 0.0,
       # for table in self.table_list
        raise NotImplementedError


    def save_tables_to_excel(self,filename):

        os.makedirs(self.excel_path, exist_ok=True)
        filepath=os.path.join(self.excel_path, f"{filename}.xlsx")

        with pd.ExcelWriter(filepath) as writer:
            # Iterate over the dictionary and write each DataFrame to a separate Excel sheet
            for i,table in enumerate(self.table_list):
                df=table.df
                   # df.columns = pd.to_datetime(df.columns.map(self.parse_quarter))
                   # add page number to title 
                df.to_excel(writer, sheet_name=f"Table {i}")
        print("Downloaded tables to excel")



class PDF_num_table(Text_PDF_extractor):
    """ Class that extract and preprocess pdf tables, assuming that the indexes are strings, the columns are dates, and the values are numbers
    
    """
    
    def __init__(self, pdf_path):
        super().__init__(pdf_path)
        pass

    
    def clean_bullets(self,df_list,function=None): # usar self df list quizas
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
    
    
    def separate_tables(self):
        """
        if the values of the table should be all numeric separate tables that contains a column of strings (this column its assumed to be another index) (assumes there are two tables in one)
        """
        raise NotImplementedError


    def create_indexes():
        pass

    def extract_dates_above_table(self,table): # camelot table object
        page_num = table.page - 1 # Page numbers in Camelot are 1-based 
        top_ypos_table=table.rows[0][0]
        x_pos_table_min=table.cols[0][0]
        x_pos_table_max=table.cols[-1][-1]

        pdf = PDFQuery(self.pdf_path)
        pdf.load(page_num)


        # Use CSS-like selectors to locate the elements
        for i in range(100):
            text_elements = pdf.pq('LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")' % (x_pos_table_min, top_ypos_table, x_pos_table_max, top_ypos_table+i)).text()
            if len(text_elements)!=0 : # breaks when finds the first text elements above the table
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
        matches = regex.findall(text_elements) # find the matches 

        return(matches)
         
        """date_results = []
 
        for match in matches:
            try:
                # Validate the matched date using datetime.strptime
                # date_obj = datetime.strptime(match, '%m/%d/%Y')  # Adjust format string as needed
                date_results.append((page_num + 1, match))  # Store page number and date string
            except ValueError:
                continue  # Skip if date format does not match"""

    def main_preprocessing_tables(self):
        """ Function that does the following steps:
            maybe filter by accuracy
            1. Separate tables
            2. clean bullets
            3. clean nans and join indexes and order rows and columns
            4. set indexes
            5. if the column header is not a date find the dates and put them as column names (the proviousley should be passed to a dataframe row)
            6. pass the numbers to a numeric dtype
        """
        raise NotImplementedError







class PDF_tables(Text_PDF_extractor):
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