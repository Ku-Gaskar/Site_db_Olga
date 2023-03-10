


from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font


import os
import re
from datetime import date
from scopus.sc_forms import DataScForm
#import io


# PATH_LOAD_DEFAULT = ''
""""
    file_stream = io.BytesIO()
    file_stream.write(b"Hello, World!")

    # Возвращаемся в начало файла, чтобы Flask мог его прочитать
    file_stream.seek(0)

    # Используйте send_file для отправки данных клиенту как файл
    return send_file(
        file_stream,
        attachment_filename='example.txt',
        as_attachment=True,
        mimetype='text/plain'
    )
"""

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

    def drawColorYellow(self,i):
        for tyty in self.ws['A'+ str(i)+':H'+ str(i)]:
            for strk in tyty:
                strk.fill = PatternFill('solid',fgColor='FFFF00')
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
            if fist_aticle != record[7]:   #('#','Название статьи',"Год","Тип публ.",'Авторы/Автор','Кафедра')
                i_index+=1
                self.ws['A'+str(i_index)]=count
                self.ws['B'+str(i_index)]=record[0]
                self.ws['C'+str(i_index)]=record[4]
                self.ws['D'+str(i_index)]=record[8]
                self.ws['E'+str(i_index)]=record[1]
                i_index+=1
                count+=1
                if (fist_aticle != record[7]) and (not record[2]) and (not record[3]):
                    self.drawColorYellow(i_index-1)
                fist_aticle=record[7]
            if not record[2]  and not record[3]:
                continue  
            self.ws['E'+str(i_index)]=record[2]
            self.ws['F'+str(i_index)]=record[3]
            i_index+=1


    def create_report_article(self, total_list):
        self.write_full_aticl(total_list)
        return save_virtual_workbook(self.wb)  

    def create_report_author(self, total_list):
        pass