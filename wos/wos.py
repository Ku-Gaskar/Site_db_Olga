from flask import Blueprint, render_template, url_for, g, request,redirect,flash,current_app,session,Response
from wos.WOS_Dbase import WOS_Dbase
from scopus.sc_forms import SC_Form,DataScForm
from flask_paginate import Pagination, get_page_parameter
from scopus.sc_excel import ScopusExportExcel
import os
from datetime import date

wos = Blueprint('wos',__name__,template_folder='templates',static_folder='static')
wos_dbase:WOS_Dbase = None

PER_PAGE=100


@wos.before_request
def before_request():
    global wos_dbase
    db=g.get('link_db')
    wos_dbase = WOS_Dbase(db)

# @scopus.teardown_request
# def teardown_request():
#     global sc_dbase
#     sc_dbase=None
#     return request


@wos.route('/', methods=['GET', 'POST'])
def index():
    content={}
    content['title']='Web of Seince'
    content['data_up'] =wos_dbase.get_data_update_wos()
    doc_sum=wos_dbase.get_doc_sum()
    content['doc_sum']=(f'{doc_sum[0]:,d}'.replace(',',' '),f'{doc_sum[1]:,d}'.replace(',',' '))
    content['h_ind'] = wos_dbase.get_h_ind()
    return render_template('wos/wos_index.j2',content = content)


@wos.route('/wos_report', methods=['GET', 'POST'])
def scopusReport():
    content={}
    content['title']='WOS - отчеты'
    limit = PER_PAGE  
    if 'wos_form_report' in session and request.method=='GET':
        form:SC_Form = SC_Form(sc_radio_auth_atcl = session['wos_form_report']['sc_radio_auth_atcl'],
                               sc_select_dep      = session['wos_form_report']['sc_select_dep'],
                               sc_select_year     = session['wos_form_report']['sc_select_year'],
                               sc_article         = session['wos_form_report']['sc_article'],
                               sc_book            = session['wos_form_report']['sc_book'],                                                  
                               sc_conf            = session['wos_form_report']['sc_conf'],
                               sc_bool_limit      = session['wos_form_report']['sc_bool_limit'],
                               sc_input_limit     = session['wos_form_report']['sc_input_limit']
                               )
    else:
        form:SC_Form = SC_Form()
    
    form.sc_select_dep.choices=[(9999,'Все кафедры')]+wos_dbase.get_nure_total_dep_list()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = 0 if page == 1 else (page-1) * limit

    if form.sc_radio_auth_atcl.data == 'author' :
        total_list=wos_dbase. select_authors_by_form(form)
        total=len(total_list)
        total_list=total_list[offset:offset+limit]
    else:
        total_list=wos_dbase.get_limit_all_article(offset,limit,form.data)
        total=wos_dbase.get_count_all_article(form.data)    
    
    if form.validate_on_submit():
        if form.sc_buttons_cancel.data:
            if 'wos_form_report' in session : session.pop('wos_form_report')
            return redirect(request.base_url)

        my_sc:DataScForm = DataScForm()
        form.populate_obj(my_sc)

        if my_sc.sc_rep_article:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            list_export=wos_dbase.get_articles_export(form.data)
            fm=f"wos_report_{date.today()}.xlsx"
            return Response(sc_exporter.create_report_article(list_export),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})            
        elif my_sc.sc_rep_authors:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            dd=form.data
            list_export=wos_dbase.get_sc_author_with_article(dd)   
            fm=f"wos_author_{date.today()}.xlsx"
            return Response(sc_exporter.create_author_with_article(list_export,dd),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})            
        elif my_sc.sc_rep_sum:
            sc_exporter:ScopusExportExcel = ScopusExportExcel()
            list_export=wos_dbase.get_sum_export()
            fm=f"wos_sum_{date.today()}.xlsx"
            return Response(sc_exporter.create_report_sum(list_export),
                            headers={'Content-Disposition': f'attachment; filename={fm}',
                                     'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})

            
        
        if my_sc.sc_buttons_ok:
            session['wos_form_report'] = form.data
            
        if my_sc.sc_buttons_search and my_sc.sc_search:
            total_list=wos_dbase.get_wos_search(my_sc)
            total=len(total_list)
            # if my_sc.sc_radio_auth_atcl == 'author' :
            #     g.sw_table='author'
            # if my_sc.sc_radio_auth_atcl == 'article' :
            #     g.sw_table='article'


    content['pagination'] = Pagination(page=page, total = total, outer_window = 0, record_name='записей',  # search=False,
                            display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                            per_page=limit, bs_version=5)
    
    content['table'] = wos_dbase.get_stamp_table_wos(f'wos_{form.sc_radio_auth_atcl.data}')
    content['table_data'] = total_list
    return render_template('wos/wos_report.j2',content = content,form = form, enumerate=enumerate)