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
import numpy as np
from collections import OrderedDict
import copy

class Image_PDF_extractor:
    def __init__(self):
        pass

    def exctract_tables(self):
        raise NotImplementedError



class Text_PDF_extractor:
    def __init__(self,pdf_path,save_path=None): # implement save path 
        self.pdf_path=pdf_path
        current_dir = os.getcwd()
        self.csv_path=os.path.join(current_dir, "data","csv")
        self.excel_path=os.path.join(current_dir, "data","excel")
        pass

    def extract_tables(self,pages="all"):
        table_list = read_pdf(self.pdf_path,pages=pages,flavor='stream',row_tol=5, strip_text='\n',edge_tol=10000,column_tol=0)#,layout_kwargs={"boxes_flow":1})
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

    
    def string_to_number(self,):


        for i,df in enumerate(self.table_list):

            df_old=df.df.copy()
            df_old = df_old.apply(pd.to_numeric, errors='ignore')
            ### clean reminiding stuff
           # df_old = df_old.apply(lambda x: x.astype(str).str.replace('_', ''))
            df_old=pd.to_numeric(df_old)
            #df_old = df_old.apply(lambda x: x.astype(str).str.replace('-', ''))
            df.df=df_old

        return(self.table_list)

    
    def clean_bullets(self,function=None): # usar self df list quizas
        "quizas implementar funciones propias por empresa..."

        for i,df in enumerate(self.table_list):
            df_old=df.df.copy()
          #  df_old = df_old.apply(lambda x: x.astype(str).str.replace('.', ''))
            df_old = df_old.apply(lambda x: x.astype(str).str.replace('(', ''))
            df_old = df_old.apply(lambda x: x.astype(str).str.replace(')', ''))
         #   df_old = df_old.apply(lambda x: x.astype(str).str.replace(',', ''))
            df_old = df_old.apply(lambda x: x.astype(str).str.replace('_', ''))
           # df_old = df_old.apply(lambda x: x.astype(str).str.replace('-', ''))
            df_old = df_old.map(lambda x: x.lower() if isinstance(x, str) else x)
            
            df.df=df_old

        return(self.table_list)
    
    def clean_str_cols(self):

        for i,df in enumerate(self.table_list):
            
            df_old=df.df.copy()
            dtypes_dict=identify_columns_types(df_old)

            for key,values in dtypes_dict.items():

                if values=="str":
                    df_old[key] = df_old[key].apply(lambda x: str(x).replace(',', ''))
                    df_old[key] = df_old[key].apply(lambda x: str(x).replace('.', ''))
                    df_old[key] =  df_old[key].apply(lambda x: str(x).replace('-', ''))

            
            df.df=df_old

        return(self.table_list)

    
    def dropnan(self):
        for i,df in enumerate(self.table_list):
            df_old=df.df.copy()

            df_old.replace(r'^\s*$', np.nan, regex=True, inplace=True)

            df_old.dropna(how="all",inplace=True,axis=1)
            df_old.dropna(how="all",inplace=True,axis=0)
            df_old.replace(np.nan,"", regex=True, inplace=True)
            df.df=df_old

        return(self.table_list)
    
    def separate_tables(self):
        """
        if the values of the table should be all numeric separate tables that contains a column of strings (this column its assumed to be another index) (assumes there are two tables in one)
        """
        table_list_aux=copy.deepcopy(self.table_list)

        for i,df in enumerate(self.table_list):

            df_old=df.df.copy()
            sep_df_list=self.separate_dataframe(df_old)
            
            df_aux=copy.deepcopy(df)
            df_aux.df=sep_df_list[0].copy()  # set first element as current element in table list
            
            table_list_aux[i]=df_aux
            sep_df_list.pop(0)

            for df_sep in sep_df_list:
                
                df_aux=copy.deepcopy(df)
                df_aux.df=df_sep
                table_list_aux.append(df_aux)

        self.table_list=copy.deepcopy(table_list_aux)
        return(self.table_list)
    

    def separate_dataframe(self,df):
        dtypes_dict=identify_columns_types(df)

        values = list(dtypes_dict.values())

        separate_table,sep_idx=structure_repeats(values, target_structure=["number","str","number"])

        if separate_table:
            sep_idx+=1
            df1 = df.iloc[:,:sep_idx].copy()
            df2 = df.iloc[:,sep_idx:].copy()
            df1_list=self.separate_dataframe(df1) # CHECK IF WORKING FINE!
            df2_list=self.separate_dataframe(df2)
            joined_list=df1_list+df2_list
            return(joined_list)
        return([df])


    def delete_no_type_cols(self):
        """
        if the values of the table should be all numeric separate tables that contains a column of strings (this column its assumed to be another index) (assumes there are two tables in one)
        """
        for i,df in enumerate(self.table_list):

            df_old=df.df.copy()

            dtypes_dict=identify_columns_types(df_old)

            for key,values in dtypes_dict.items():

                if values==None:
                    df_old = df_old.drop(key, axis=1)
                    
            df.df=df_old

        return(self.table_list)
        
    def set_zeros(self):
        for i,df in enumerate(self.table_list):

            df_old=df.df.copy()
            for idx, (index, row) in enumerate(df_old.iterrows()):
                if index != "":
                    for col in df_old.columns:
                        if row[col]=="":
                            df_old.at[index, col] = 0
            df.df=df_old

        return(self.table_list)
    
    def create_indexes(self):
        for i,df in enumerate(self.table_list):

            df_old=df.df.copy()

            dtypes_dict=identify_columns_types(df_old)

            first_item=next(iter(dtypes_dict.items()))

            first_col=first_item[1]

            if first_col=="str":
                
                col_name=first_item[0]
                df_old=df_old.set_index(col_name)
                    
            df.df=df_old

        return(self.table_list)
    


    def set_headers_to_tables(self):
        # asume que camelot nunca pone columns headers y indices 
        for i,df in enumerate(self.table_list):

            if not self.is_date_in_df(df.df):
                dates_list=self.extract_dates_above_table(df)
                if len(dates_list)==df.df.shape[1]:
                    df.df.columns=dates_list
            
        return(self.table_list)
    
    def is_date_in_df(self,df):
        # Not implemented yet
        return(False)

    def extract_dates_above_table(self,table): # camelot table object
        page_num = table.page - 1 # Page numbers in Camelot are 1-based 
        top_ypos_table=table.rows[0][0]
        x_pos_table_min=table.cols[0][0]
        x_pos_table_max=table.cols[-1][-1]

        pdf = PDFQuery(self.pdf_path)
        pdf.load(page_num)

        date_patterns = [
            r'\d{1,2}.\d{1,2}.\d{2,4}', #match any single character xx-xx-xxxx or x-x-xxxx
            r'\d{2,4}.\d{1,2}.\d{1,2}',     #match xxxx-xx-xx  or 
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # 31 Jan 2023
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',  # Jan 31, 2023
            #r'\b(January|February|March|April|May|June|July|August|September|October|November|December) (0?[1-9]|[12][0-9]|3[01]), (\d{4})\b',
            #r'\b(0?[1-9]|[12][0-9]|3[01]) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})\b',
            #r'\b(0?[1-9]|[12][0-9]|3[01]) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de (\d{4})\b',
        ]

        # Compile regex patterns
        regex = re.compile('|'.join(date_patterns))
        # Use CSS-like selectors to locate the elements
        for i in range(500):
            text_elements = pdf.pq('LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")' % (x_pos_table_min, top_ypos_table, x_pos_table_max, top_ypos_table+i)).text()
           # pattern = re.compile(r'\S')
            matches = regex.findall(text_elements) # find the matches 
            if len(matches)!=0:
                return(matches)
            # Count non-empty and non-whitespace strings
          #  non_empty_non_space_count = len([s for s in text_elements if pattern.search(s)])


        return([])

    def main_preprocessing_tables(self):
        """ Function that does the following steps:
            maybe filter by accuracy

            1. clean bullets
            2. clean the , or . in the non numbers columns
            2. identify columns types number or letters
            3. delete no type columns
            3. separate tables if necesary
            4
            5. "" to nan and dropnans cols and rows  
            6. drop no number or string colums, and check the structure str - numbr - numbr - numbr (before checking the structure ensure that index is cualquier cosa)
            7. see index and set  or cols header if none find date, if date do none, if other bajar as column
            8.   
        """
        self.clean_bullets()
        self.clean_str_cols()
        self.delete_no_type_cols()
        self.separate_tables()
       # self.string_to_number()
        self.dropnan()
        self.create_indexes()
        self.set_zeros()
        self.dropnan() # in the number types change to 0... 
        # aca falta join indexes...
        self.set_headers_to_tables()
        return(self.table_list)
    
def identify_columns_types(df): # pandas dataframe with ALL strings

    dtype_dict = OrderedDict()
    for col_name,col in df.items():
        
        letters=col.apply(lambda x: count_letters(x))
        numbers=col.apply(lambda x: count_numbers(x))
        max_numbers=numbers.max() # por fila
        max_letters=letters.max() # por fila
        letters=letters.sum()
        numbers=numbers.sum()
        ratio=numbers/(letters+0.01)

        if ratio>2 and numbers>5 and max_numbers>3: #trshold de numbers para que sea considerado una columna
            dtype_dict[col_name]="number"

        elif letters>10 and max_letters>4:
            dtype_dict[col_name]="str"
        
        else:
            dtype_dict[col_name]=None
    return(dtype_dict)
        
    

def count_letters(text):
    return len(re.findall(r'[a-zA-Z]', text))

def count_numbers(text):
    return len(re.findall(r'\d', text))

# Check if the structure repeats
def structure_repeats(values, target_structure):
    len_target = len(target_structure)
    len_values = len(values)
    
    for i in range(len_values - len_target + 1):
        if values[i:i+len_target] == target_structure:
            return True,i
    return False,None


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



if __name__=="__main__":
    pdf_path="Estados_financieros_2010_03-páginas.pdf"
    pdf_path="IFS 1Q24.pdf"

    pdf_instance=PDF_num_table(pdf_path)
    tables=pdf_instance.extract_tables(pages="3")
    new_tables=pdf_instance.main_preprocessing_tables()
    pdf_instance.save_tables_to_excel(filename="excel_test")
