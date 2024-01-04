
from flask import Blueprint, render_template, url_for, g, request,redirect,flash,current_app,session,Response 
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
# from werkzeug.datastructures import FileStorage 
import threading


from io import TextIOBase 

# from flask_socketio import emit
# from init_app import socketio
from init_app import get_db

import json


import os
import csv
import re

from datetime import date

import app_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from .elseveir_read_metrics import process_record, set_config_elsevir


from chromedriver_py import binary_path # this will get you the path variable



from scopus.SC_Dbase import SC_Dbase
from scopus.sc_forms import SC_Form,DataScForm
from scopus.sc_excel import ScopusExportExcel

scopus=Blueprint('scopus',__name__,template_folder='templates',static_folder='static')
sc_dbase:SC_Dbase = None

PER_PAGE=100

logger=app_logger.get_logger(__name__)

# словарь для прогресс бара
scUpdateDocCitH={'start':False, 'id_current':None,'max':0, 'min':0, 'curent':0, 'authorName':None, 'data':{}}
#??????????????????????????????????????????????????????????
# socketio = SocketIO()

# def init_socketio(app):
#     socketio.init_app(app)

# # Обработчик события SocketIO для Blueprint'а
# @socketio.on('update_database', namespace='/my_namespace')
# def handle_my_event(data):
#     print('Received data: {}'.format(data))
#     emit('update_progress', {'data': 'Response data'}, namespace='/my_namespace')


# # Регистрируем обработчики событий в Blueprint'е
# socketio.on('update_database', namespace='/my_namespace')(handle_my_event)

#??????????????????????????????????????????????????????????

@scopus.before_request
def before_request():
    global sc_dbase
    # db=g.get('link_db')
    sc_dbase = SC_Dbase(get_db())


@scopus.route('/', methods=['GET', 'POST'])
@scopus.route('/index', methods=['GET', 'POST'])
def index():
    content={}
    content['title']='Scopus'
    content['data_up'] = sc_dbase.get_data_update_scopus()
    content['progress'] = scUpdateDocCitH
    doc_sum=sc_dbase.get_doc_sum()
    if doc_sum[0]: 
        content['doc_sum']=(f'{doc_sum[0]:,d}'.replace(',',' '),f'{doc_sum[1]:,d}'.replace(',',' '))
        content['h_ind'] = sc_dbase.get_h_ind()
    else:
         content['doc_sum']=('0','0')
         content['h_ind'] ='0'
    if current_user.is_authenticated:
        content['login']= current_user._UserLogin__user['name'] +'/выход'
        content['login_href'] = url_for('logout',next='/scopus/')
    else:
        content['login']= 'Авторизация'
        content['login_href'] = url_for('login',next='/scopus/')        
     
    return render_template('scopus/sc_index.html',content = content)


@scopus.route('/sc_report', methods=['GET', 'POST'])
def scopusReport():
    content={}
    content['title']='Scopus - отчеты'
    limit = PER_PAGE  
    if 'sc_form_report' in session and request.method=='GET':
        form:SC_Form = SC_Form(sc_radio_auth_atcl = session['sc_form_report']['sc_radio_auth_atcl'],
                               sc_select_dep      = session['sc_form_report']['sc_select_dep'],
                               sc_select_year     = session['sc_form_report']['sc_select_year'],
                               sc_article         = session['sc_form_report']['sc_article'],
                               sc_book            = session['sc_form_report']['sc_book'],                                                  
                               sc_conf            = session['sc_form_report']['sc_conf'],
                               sc_bool_limit      = session['sc_form_report']['sc_bool_limit'],
                               sc_input_limit     = session['sc_form_report']['sc_input_limit']
                               )
    else:
        form:SC_Form = SC_Form()
    
    form.sc_select_dep.choices=[(9999,'Все кафедры')]+sc_dbase.get_nure_total_dep_list()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = 0 if page == 1 else (page-1) * limit

    if form.sc_radio_auth_atcl.data == 'author' :
        total_list=sc_dbase.select_authors_by_form(form)
        total=len(total_list)
        total_list=total_list[offset:offset+limit]
    else:
        total_list=sc_dbase.get_limit_all_article(offset,limit,form.data)
        total=sc_dbase.get_count_all_article(form.data)    
    
    if form.validate_on_submit():
        if form.sc_buttons_cancel.data:
            if 'sc_form_report' in session : session.pop('sc_form_report')
            return redirect(request.base_url)

        my_sc:DataScForm = DataScForm()
        form.populate_obj(my_sc)

        if my_sc.sc_rep_article:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            list_export=sc_dbase.get_articles_export(form.data)
            fm=f"sc_report_{date.today()}.xlsx"
            return Response(sc_exporter.create_report_article(list_export),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})            
        elif my_sc.sc_rep_authors_with_stat:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            list_export=sc_dbase.select_authors_by_form(form)
            fm=f"sc_report_author_{date.today()}.xlsx"
            return Response(sc_exporter.create_report_authors_with_stat(list_export),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})            
        elif my_sc.sc_rep_authors:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            dd=form.data
            list_export=sc_dbase.get_sc_author_with_article(dd)   
            fm=f"sc_author_{date.today()}.xlsx"
            return Response(sc_exporter.create_author_with_article(list_export,dd),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})            
        elif my_sc.sc_rep_sum:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            list_export=sc_dbase.get_sum_export()
            fm=f"sc_sum_{date.today()}.xlsx"
            return Response(sc_exporter.create_report_sum(list_export),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})
                    
        if my_sc.sc_buttons_ok:
            session['sc_form_report'] = form.data
            
        if my_sc.sc_buttons_search and my_sc.sc_search:
            total_list=sc_dbase.get_sc__search(my_sc)
            total=len(total_list)

    content['pagination'] = Pagination(page=page, total=total,outer_window=0,record_name='записей',   #search=False,
                            display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                            per_page=limit, bs_version=5)
    
    content['table'] = sc_dbase.get_stamp_table(form.sc_radio_auth_atcl.data)
    content['table_data'] = total_list
    return render_template('scopus/sc_report.j2',content = content,form = form, enumerate=enumerate)

# @socketio.on('update_database',namespace='/update_database')
# def handle_update_database():
#     import time
#     for i in range(1, 101):
#         time.sleep(0.1)  # Имитация длительной работы
#         emit('update_progress', {'progress': i,'textProgress':"ПРивет  "+str(i)}, namespace='/update_database')


@scopus.route('/progressUpdate', methods=['GET', 'POST'])
def progress_update():
    global scUpdateDocCitH
    author=None
    if scUpdateDocCitH['id_current']:
        author=sc_dbase.get_author_by_id(scUpdateDocCitH['id_current'])
    if author:
        scUpdateDocCitH['authorName']=author[0][1]   
    json_data = json.dumps(scUpdateDocCitH)
    return Response(json_data, status=200, mimetype='application/json')

# обновление метрик одного автора
@scopus.route('/update_metric', methods=['GET','POST'])
def update_metric():
    data = {}
    if 'scopus_id' in request.json:
        scopus_id = request.json['scopus_id'].strip()
        author_id = request.json['author_id'].strip()
    else:
        data['err'] = 'Нет scopus_id в запросе'
    if scopus_id:
        client = set_config_elsevir()
        read_author , metric = process_record(client, scopus_id)
        if read_author:
            data = {'doc': metric['coredata']['document-count'],
                      'note': metric['coredata']['citation-count'],
                       'h_index': metric['h-index']
                       }  
            try:        
                sc_dbase.update_cit_doc_hIndex(data,(author_id, scopus_id))
                data['err'] = None
            except:
                data['err'] = 'Ошибка записи в БД'
        else:
            data['err'] = 'Ошибка чтения из Elsevir.  scopus_id=' + scopus_id
    else:
        data['err'] = 'Scopus_id отсутствует'
    
    return Response(json.dumps(data), status=200, mimetype='application/json')


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# функция для запуска в фоновом режиме 
def update_database(app):
    global scUpdateDocCitH
    # global sc_dbase
    # global sc_dbase
    # with SC_Dbase(db) as sc_dbase:
    with app.app_context():

      
        sc_dbase = SC_Dbase(get_db())

        list_scopus_id=sc_dbase.get_list_scopusID()
        client = set_config_elsevir()

        content={}
        content['title']='Scopus - Update'

     # ver. == 4.8.0
        # chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        # driver = webdriver.ChromeOptions(chrome_options=chrome_options) 
    # ver. == 4.8.0
        
    # ver. == 4.15.2
        # svc = webdriver.ChromeService(executable_path=binary_path) #изменения 10.12.23 
        # driver = webdriver.Chrome(service=svc)                     #изменения 10.12.23 

        # driver = webdriver.Chrome()
    # ver. == 4.15.2
        
        
        if not list_scopus_id:
            flash("Ошибка обновления БД Scopus.Нет данных БД ХНУРЕ", "error")
            return redirect('./') 
        
        scUpdateDocCitH['start'] = True
        scUpdateDocCitH['max']=len(list_scopus_id)

        for count_i,item in enumerate(list_scopus_id):
            item=list(item)
            read_author , metric = process_record(client, item[1])
            if not read_author:
                print (f"scopus_id недействителен: {item[1]}")
                logger.warning(f"scopus_id недействителен  id_author={item[0]}; ID---> '{item[1]}'")
                continue
            author = {'doc': metric['coredata']['document-count'],
                      'note': metric['coredata']['citation-count'],
                       'h_index': metric['h-index']
                       }    
            scUpdateDocCitH['id_current'] = item[0]
            scUpdateDocCitH['curent'] = count_i
            scUpdateDocCitH['data'] = author


            # url=f'https://www.scopus.com/authid/detail.uri?authorId={item[1]}' 
            # driver.implicitly_wait(20)  # Установить 20 секунд времени ожидания
            # try:
            #     driver.get(url)
            # except:
            #     print (f"URL недействителен: {url}")
            #     logger.warning(f"URL недействителен  id_author={item[0]}; URL---> '{url}'")
            #     continue  
            # try:
            #     WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.ID,'authorDetailsPage'))) 
            # except:
            #     print (f"Страница не загружена: {url}")
            #     logger.warning(f"Страница не загружена: id_author={item[0]}; URL---> '{url}'")
            #     continue          
            # try:
            #     #
            #     s1_citir=driver.find_element(By.CSS_SELECTOR,'div[data-testid="metrics-section-citations-count"] span[data-testid="unclickable-count"]')            
            #     author={}
            #     if s1_citir:
            #         if item[2] == 'None': item[2] ='0'
            #         author['note'] = s1_citir.text.replace(' ','')
            #     s1_doc=driver.find_element(By.CSS_SELECTOR,'div[data-testid="metrics-section-document-count"] span[data-testid="unclickable-count"]')            
            #     if s1_doc:
            #         if item[3] == 'None': item[3] ='0'
            #         author['doc'] = s1_doc.text.replace(' ','')

            #     s1_h_index=driver.find_element(By.CSS_SELECTOR,'div[data-testid="metrics-section-h-index"] span[data-testid="unclickable-count"]')            
            #     if s1_h_index:
            #         if item[4] == 'None': item[4] ='0'
            #         author['h_index']=s1_h_index.text.replace(' ','')

            # scUpdateDocCitH['id_current']=item[0]
            # scUpdateDocCitH['curent']=count_i
            # scUpdateDocCitH['data']=author
                
                # # !!!!!!!!!!!!!!!!!!!!!!!!!!!
                # emit('update_progress', {'progress': int((count_i*100)/len(list_scopus_id)),'textProgress':
                #                          f"id={item[0]}: документов:{author['doc']} цитирования:{author['note']} h-index:{author['h_index']}"}, namespace='/update_database')
                # # !!!!!!!!!!!!!!!!!!!!!!!!!!!
                
            if (int(author['note']) < int(item[3])) or (int(author['doc']) < int(item[2])) or (int(author['h_index']) < int(item[4].split(".")[0])):
                    str_warning=f"""Предупреждение - данные уменьшены id={item[0]}:
                                                            цитирования: {item[3]} -> {author['note']};  
                                                            документов: {item[2]} -> {author['doc']};
                                                                h-index: {item[4]} -> {author['h_index']} """
                    logger.warning(str_warning)
                    print (str_warning)
            elif (int(author['note']) == int(item[3])) and (int(author['doc']) == int(item[2])) and (int(author['h_index']) == int(item[4].split('.')[0])):
                    continue
            try:        
                sc_dbase = SC_Dbase(get_db())
                sc_dbase.update_cit_doc_hIndex(author,item)
            except:  
                logger.warning(f"Ошибка записи в бд: id_author={item[0]}; scopus_id---> '{item[1]}'")
                print(f"Ошибка записи в бд: id_author={item[0]}; scopus_id---> '{item[1]}'")
                continue             
    # driver.close()
    scUpdateDocCitH['start']=False
    # flash("Вы успешно обновили данные авторов БД Scopus", "success")

@scopus.route('/sc_update_DocCitH')
# @socketio.on('update_database',namespace='/update_database')
# @login_required 
def sc_update_DocCitH():
    global scUpdateDocCitH
    global sc_dbase
    if scUpdateDocCitH['start']:
        flash("Процесс обновления авторов БД Scopus уже запущен", "info")
        return redirect('./')

    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next='/scopus/'))

    thread = threading.Thread(target=update_database,args=(current_app._get_current_object(),))
    thread.start()
    flash("Процесс обновления авторов БД Scopus запущен", "info")
    return redirect('./') 


@scopus.route('/export_green_table')
def export_green_table():
    sc_exporter:ScopusExportExcel = ScopusExportExcel()
    list_export=sc_dbase.get_full_data_export()
    
    fm=f"Table_Green_{date.today()}.xlsx"
    return Response(sc_exporter.create_green_table(list_export),
                    headers={'Content-Disposition': f'attachment; filename={fm}',
                             'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})    


@scopus.route('/upload', methods=['POST','GET'])
# @login_required 
def upload_file():
    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next='/scopus/'))  #request.full_path))
    
    def data_preparation(one_autor):
        data=['']*12
        data[0]=re.findall(r'eid=(2-s2.0-[0-9]{8,15})[&]?',one_autor)[0]    # eid
        data[1]=re.findall(r'title=\{(.*)\}',one_autor)[0]                  # title
        data[2]=re.findall(r'journal=\{(.*)\}',one_autor)[0]                # journal
        data[3]=re.findall(r'year=\{(.*)\}',one_autor)[0]                   # year
        data[11]=re.findall(r'author=\{(.*)\}',one_autor)[0]
        if 'volume={' in one_autor:
            data[4]=re.findall(r'volume=\{(.*)\}',one_autor)[0]
        if 'number={' in one_autor:
            data[5]=re.findall(r'number=\{(.*)\}',one_autor)[0]
        if 'pages={' in one_autor: 
            data[6]=re.findall(r'pages=\{(.*)\}',one_autor)[0]
        if 'doi={' in one_autor: 
            data[7]=re.findall(r'doi=\{(.*)\}',one_autor)[0]
        if 'note={' in one_autor: 
            data[8]=re.findall(r'note=\{cited By (.*)\}',one_autor)[0]
        if 'publisher={' in one_autor: 
            data[9]=re.findall(r'publisher=\{(.*)\}',one_autor)[0]
        if 'document_type={' in one_autor: 
            data[10]=re.findall(r'document_type=\{(.*)\}',one_autor)[0]
        return data

    def sc_update_bib(file:TextIOBase):
        buff = file.read()
        for One_Autor in buff.split("@"):
            if len(One_Autor) < 40: continue  
            if not sc_dbase.update_article(data_preparation(One_Autor)):
                return False            
        return True

    def sc_update_csv(file:TextIOBase):
        buff = csv.reader(file)
        for i,One_Autor in enumerate(buff):            
            if i==0: continue 
            eid = One_Autor[2]
            if not eid: continue
            for id_autor in One_Autor[0].split(';'):
                if not id_autor: continue 
                if not sc_dbase.update_sc_in_autors(id_autor,eid):
                    return False
        return True
    
    files =  request.files.getlist('sc_load_files[]')
    for file in files:
        file.save('./scopusData/' + secure_filename(file.filename))

    for file_ in files:
        file_filename=secure_filename(file_.filename)
        file :TextIOBase = open('./scopusData/' + file_filename,encoding='utf-8')    
        if file_filename[-3:] == 'bib':
            if not sc_update_bib(file): 
                flash(f"Файл '{file_filename}': ошибка обработки", "error")
                file.close()
                return redirect('index') 
            
        elif file_filename[-3:]== 'csv':
            if not sc_update_csv(file):
                flash(f"Файл '{file_filename}': ошибка обработки", "error")
                file.close()                
                return redirect('index') 
        else:
            flash(f"Файл '{file_filename}' не соответствует формату", "error")
            continue
        
        file.close()
        if os.path.exists('./scopusData/'+ file_filename):
            os.remove('./scopusData/'+ file_filename)        

    flash("Вы успешно обновили статьи БД Scopus", "success")
    return redirect('index') 


@scopus.route('/deteteArticleScopus')
# @login_required 
def deteteArticleScopus ():
    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next='/scopus/'))  #request.full_path))

    sc_dbase.deleteArticle()
    flash("Вы успешно удалили статьи БД Scopus", "success")
    return redirect('index') 
