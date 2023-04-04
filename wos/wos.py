from flask import Blueprint, render_template, url_for, g, request,redirect,flash,current_app,session,Response
from wos.WOS_Dbase import WOS_Dbase
from scopus.sc_forms import SC_Form,DataScForm
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename


from scopus.sc_excel import ScopusExportExcel
import os
from datetime import date
from io import TextIOBase  
import re
import app_logger


wos = Blueprint('wos',__name__,template_folder='templates',static_folder='static')
wos_dbase:WOS_Dbase = None

logger=app_logger.get_logger(__name__)

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
@wos.route('/index', methods=['GET', 'POST'])
def index():
    content={}
    content['title']='Web of Seince'
    content['data_up'] =wos_dbase.get_data_update_wos()
    doc_sum=wos_dbase.get_doc_sum()
    if doc_sum[0]: 
        content['doc_sum']=(f'{doc_sum[0]:,d}'.replace(',',' '),f'{doc_sum[1]:,d}'.replace(',',' '))
        content['h_ind'] = wos_dbase.get_h_ind()
    else:
         content['doc_sum']=('0','0')
         content['h_ind'] ='0'
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

@wos.route('/upload', methods=['POST','GET'])
@login_required 
def upload_file():
    
    #----------------------------------------------------------------
    def search_in_table_hnure_for_author(author,orcid):
        if orcid:
            id_author=wos_dbase.select_idAuthor_by_orcid(orcid)
            if id_author: return  id_author        
        return wos_dbase.select_idAuthor_by_latName(author)
    #----------------------------------------------------------------
    def data_preparation(one_autor:str):
        #-- - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - -
        def find_one(one_:str,name:str):
            #request=f"^{name} = "+chr(92)+"{([\s\S]+?*)\}"
            patern='\n'+name+' = {'
            start=one_.find(patern)
            if start==-1: return ''
            start+=len(patern)
            end=one_.find('}',start)
            return one_[start:end].replace('   ',' ').replace('  ',' ').replace('\n','')
        #-- - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - -
        LIST_columns=('Unique-ID','Title','Journal','Year','Author','Volume','Number','Pages','DOI','Times-Cited',
              'Publisher','Type')
        LIST_id=('ResearcherID-Numbers','ORCID-Numbers')
            #f_str=re.findall("^"+name+r"\{([\s\S]+?*)\}",one_)
            #return f_str[0].replace('\n','').replace('  ',' ') if f_str else '
        data=[]    
        for name in LIST_columns:
            data.append(find_one(one_autor,name))

        researcher_dict=dict(re.findall(r'([\w]+, [\w]+).{0,}?/([A-Za-z]{1,}-[0-9]{3,}-[0-9]{4})',find_one(one_autor,LIST_id[0])))
        orcid_dict=dict(re.findall(r'([\w]+, [\w]+).{0,}?/([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4})',find_one(one_autor,LIST_id[1])))    
        return data,researcher_dict,orcid_dict

    def wos_update_bib(file:TextIOBase):
        buff=file.read()
        for One_Autor in buff.split("@"):
            if len(One_Autor)<40: continue
            data1=data_preparation(One_Autor)
            data, r_id, r_orcid = data1
            id_article=wos_dbase.insert_article(data)
            if id_article:
                for author in data[4].split(" and "):
                    author_orcid,author_r_id='',''
                    if author in r_orcid: author_orcid=r_orcid[author]   
                    if author in r_id: author_r_id=r_id[author]
                    author_id_hnure = search_in_table_hnure_for_author(author,author_orcid) 
                    if  len(author_id_hnure) > 1:
                        logger.warning(f"ERROR: more than 1 -> {len(author_id_hnure)} :\n{data[0]} --> {author_id_hnure}")
                        #print(f"ERROR: more than 1 -> {len(author_id_hnure)} :\n{author_id_hnure}")
                        
                        author_id_hnure=int(author_id_hnure[0][0])
                    elif len(author_id_hnure)==1:
                        author_id_hnure=int(author_id_hnure[0][0])
                    else: 
                        author_id_hnure=None

                    wos_dbase.insert_author_in_table_wosAutors((data[0],author_orcid ,author_r_id,author,author_id_hnure)) 
            else: 
                wos_dbase.update_note((data[9],data[0]))
            # print (id_article)
        return True

    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next=request.full_path))
    
    if request.method == 'GET':
        flash("Статьи не обновлены! Повторите процедуру обновления.", "error")
        return redirect('index') 
    
    files =  request.files.getlist('wos_load_files[]')
    for file in files:
        file.save('./wos/wosData/' + secure_filename(file.filename))

    for file_ in files:
        file_filename=secure_filename(file_.filename)
        file :TextIOBase = open('./wos/wosData/' + file_filename,encoding='utf-8')    
        if (file_filename[-3:] == 'bib') and ('savedrecs' in file_filename):
            if not wos_update_bib(file): 
                 flash(f"Файл '{file_filename}': ошибка обработки", "error")
                 file.close()
                 return redirect('index')             
        
        file.close()
        if os.path.exists('./wos/wosData/'+ file_filename):
            os.remove('./wos/wosData/'+ file_filename)        

    flash("Вы успешно обновили статьи БД WOS", "success")
    return redirect('index') 

@wos.route('/deteteArticleWOS')
@login_required 
def deteteArticleWOS():
    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
    wos_dbase.deleteArticle()
    flash("Вы успешно удалили статьи БД WOS", "success")
    return redirect('index') 