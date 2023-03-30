from flask import Blueprint, render_template, url_for, g, request,redirect,flash,current_app,session,send_file,Response
from scopus.SC_Dbase import SC_Dbase
from scopus.sc_forms import SC_Form,DataScForm
from flask_paginate import Pagination, get_page_parameter
from scopus.sc_excel import ScopusExportExcel
import os
from datetime import date
import app_logger
from flask_login import login_required,current_user

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


scopus=Blueprint('scopus',__name__,template_folder='templates',static_folder='static')
sc_dbase:SC_Dbase = None


PER_PAGE=100

logger=app_logger.get_logger(__name__)


@scopus.before_request
def before_request():
    global sc_dbase
    db=g.get('link_db')
    sc_dbase = SC_Dbase(db)

# @scopus.teardown_request
# def teardown_request():
#     global sc_dbase
#     sc_dbase=None
#     return request


@scopus.route('/', methods=['GET', 'POST'])
def index():
    content={}
    content['title']='Scopus'
    content['data_up'] =sc_dbase.get_data_update_scopus()
    doc_sum=sc_dbase.get_doc_sum()
    content['doc_sum']=(f'{doc_sum[0]:,d}'.replace(',',' '),f'{doc_sum[1]:,d}'.replace(',',' '))
    content['h_ind'] = sc_dbase.get_h_ind()
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
            # if my_sc.sc_radio_auth_atcl == 'author' :
            #     g.sw_table='author'
            # if my_sc.sc_radio_auth_atcl == 'article' :
            #     g.sw_table='article'


    content['pagination'] = Pagination(page=page, total=total,outer_window=0,record_name='записей',   #search=False,
                            display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                            per_page=limit, bs_version=5)
    
    content['table'] = sc_dbase.get_stamp_table(form.sc_radio_auth_atcl.data)
    content['table_data'] = total_list
    return render_template('scopus/sc_report.j2',content = content,form = form, enumerate=enumerate)

@scopus.route('/sc_update_DocCitH')
@login_required 
def sc_update_DocCitH():
    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next=request.full_path))

    content={}
    content['title']='Scopus - Update'
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    list_scopus_id=sc_dbase.get_list_scopusID()
    for item in list_scopus_id:
        url=f'https://www.scopus.com/authid/detail.uri?authorId={item[1]}' 
        driver.implicitly_wait(20)  # Установить 20 секунд времени ожидания
        try:
            driver.get(url)
        except:
            print (f"URL недействителен: {url}")
            logger.warning(f"URL недействителен  id_author={item[0]}; URL---> '{url}'")
            continue  
        try:
            WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.ID,'highcharts-information-region-1'))) 
        except:
            print (f"Страница не загружена: {url}")
            logger.warning(f"Страница не загружена: id_author={item[0]}; URL---> '{url}'")

            continue          

        try:
            s1=driver.find_elements(By.CSS_SELECTOR,'span[data-testid="unclickable-count"]')            
            if s1:
                author={'note':s1[0].text.replace(' ',''),'doc':s1[1].text.replace(' ',''),'h_index':s1[2].text.replace(' ','')}
                if (int(author['note']) < int(item[3])) or (int(author['doc']) < int(item[2])) or (int(author['h_index']) < int(item[4])):
                    str_warning=f"""Предупреждение  данные уменьшены id={item[0]}: цитирования  {item[3]} -> {author['note']};  
                                                                        документов: {item[2]} -> {author['doc']};
                                                                        h-index: {item[4]} -> {author['h_index']} """
                    logger.warning(str_warning)
                    print (str_warning)
                elif (int(author['note']) == int(item[3])) and (int(author['doc']) == int(item[2])) and (int(author['h_index']) == int(item[4])):
                    continue

                sc_dbase.update_cit_doc_hIndex(author,item[0])

        except:  
            logger.warning(f"Запись не обновлена: id_author={item[0]}; URL---> '{url}'")
            print(f"Запись не обновлена: id_author={item[0]}; URL---> '{url}'")
            continue             
    
    driver.close()

    return render_template('base.j2',content=content)

@scopus.route('/export_green_table')
def export_green_table():
    sc_exporter:ScopusExportExcel = ScopusExportExcel()
    list_export=sc_dbase.get_full_data_export()
    
    fm=f"Table_Green_{date.today()}.xlsx"
    return Response(sc_exporter.create_green_table(list_export),
                    headers={'Content-Disposition': f'attachment; filename={fm}',
                             'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})

   