
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
import os
import re
from datetime import date
from scopus.sc_forms import DataScForm


# PATH_LOAD_DEFAULT = ''


#----------------------------------------------------------------
class ExportExcel():
   
    def __init__(self,path=''):
   
        self.all_title=('#','Название статьи',"Год","Тип публ.",'Авторы/Автор','Кафедра')
        self.mas_Doc=(4.0, 80.0, 10.0, 10, 55.0, 13.0)
        self.mas_Doc_Name=('#','Название статьи','Авторы','Цитирования')
        self.bd = Side(style='thick', color="000000")
        self.bl = Side(style='thin', color="000000")
   
        if not path:
            self._path = os.getcwd()
        else:
            self._path = path
        self.wb : Workbook  = Workbook()
        self.ws : Worksheet = self.wb.active
            
    def close_book(self):
        current_date = str(date.today())
        i=1
        Namefile = f'{self._path}/scopus_report_{current_date}.xlsx'
        Name_=Namefile[:-5]
        while os.path.isfile(Namefile):
            Namefile=f"{Name_}({str(i)}).xlsx"
            i+=1
        self.wb.save(Namefile)
        self.wb.close()
 
    def set_Header(self,i_row,Doc_Name):
     for i_col,val in enumerate(Doc_Name):
        adr=get_column_letter(i_col+1)+str(i_row)
        self.ws[adr].value = val
        self.ws[adr].alignment =Alignment(horizontal='center',vertical='center')
        self.ws[adr].font = Font(bold=True)
        self.ws[adr].border = Border(left=self.bd, top=self.bd, right=self.bd, bottom=self.bd)

    def set_Width(self,d):
        for i,val in enumerate(d):
            self.ws.column_dimensions[get_column_letter(i+1)].width = val
#----------------------------------------------------------------

class ScopusExportExcel(ExportExcel):

    def write_full_aticl(self,total_list):
        self.ws.title ='ALL_Aticles'
        self.set_Width(self.mas_Doc)
        self.set_Header(1,self.all_title)
        fist_aticle=''
        i_index=1
        count=1 
        for record in total_list:
            if fist_aticle != record[1]:   #('#','Название статьи',"Год","Тип публ.",'Авторы/Автор','Кафедра')
                i_index+=1
                self.ws['A'+str(i_index)]=count
                self.ws['B'+str(i_index)]=record[1]
                self.ws['C'+str(i_index)]=record[3]
                self.ws['D'+str(i_index)]=record[4]
                self.ws['E'+str(i_index)]=record[2]
                i_index+=1
                count+=1
                fist_aticle=record[1]
            self.ws['E'+str(i_index)]=record[6]
            self.ws['F'+str(i_index)]=record[7]
            i_index+=1


    def create_report_article(self, total_list):#my_sc:DataScForm):
        self.write_full_aticl(total_list)
        self.close_book()

    def create_report_author(self, total_list):#my_sc:DataScForm):
        pass
        # self.write_full_aticl(total_list)
        # self.close_book()