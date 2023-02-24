from flask import Flask, render_template, url_for, g, request, Blueprint,redirect,flash

from flask_bootstrap import Bootstrap
from FDataBase import FDataBase
import psycopg2
from flask_paginate import Pagination, get_page_parameter
import forms


DATABASE='localhost'
PORT = '5432'
DEBUG=True
SECRET_KEY='trwyuwteutweur376437643764kjf'

PER_PAGE=100     # записей на одной странице nure
NOT_DEP=10000    # id кафедры которой нет

app = Flask(__name__)
app.config.from_object(__name__)


#Bootstrap(app)

def connect_db():
    conn = psycopg2.connect( host=DATABASE, port=PORT, user="postgres", password="postgress")
    return conn

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

def update_db_author(cont,d,id):
    a,b,c = True, True, True 
    if id == 0:
        return True if dbase.insert_new_author(d) else False
    # обработка кафедр ----------------------------------------------
    # list_id_dep_old =  dbase.get_dep_by_author(int(id))
    a=dbase.delete_dep_by_id_author(id)
    a=dbase.insert_dep_by_id_author(id,cont['author'][0][1],d.depat)
    if d.part_time_worker:
        a=dbase.insert_dep_by_id_author(id,cont['author'][0][1],d.depat_two)

    # if list_id_dep_old[0][3] != d.depat:
    #     a=dbase.update_dep_by_id(id,d.depat,list_id_dep_old[0][3])
    # if (len(list_id_dep_old) == 1 ) and (d.depat_two != NOT_DEP):
    #     a=dbase.insert_dep_by_id_author(id,cont['author'][0][1],d.depat_two)
    # elif (len(list_id_dep_old) == 2) and (d.depat_two == NOT_DEP):
    #     a=dbase.delete_dep_by_id_author(id,list_id_dep_old[1][3])
    # elif (len(list_id_dep_old) == 2) and (d.depat_two != NOT_DEP) and (d.depat_two != list_id_dep_old[1][3]):
    #     a=dbase.update_dep_by_id(id,d.depat_two,list_id_dep_old[1][3])
    #----------------------------------------------------------------    
    if (cont['author'][0][1] != d.name_author) or (cont['author'][0][3] != d.scopus_id) or (cont['author'][0][4] != d.orcid_id
        ) or (cont['author'][0][5] != d.researcher_id):
        b=dbase.update_name_scopus_orcid_reasearcher_id_by_author_id(d,cont)
    if cont['author'][0][6]!= d.list_lat_name:
        dbase.delete_lat_name_by_id_author(id)
        name_lat_dict = {}
        for lat_name in d.list_lat_name.split(';'):
            name_lat_dict[lat_name.strip()] = id
        for key,id_name in name_lat_dict.items():
            c=dbase.insert_lat_name_by_author_id(key,id_name)

    return True if a and b  and c else False 

dbase=None

@app.before_request
def before_request():
    global dbase
    dbase = FDataBase(get_db())


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.j2',content = {'title':'Генератор отчетов'})


@app.route("/hnure/<int:cur_page>",methods=['GET','POST']) 
def edit_author(cur_page):
    def set_form_edit(content:dict={'author':[(None,'','','','','','')]}):
        if (cur_page!=0):
            edit_form.name_author.data=content['author'][0][1]
            edit_form.scopus_id.data=content['author'][0][3]
            edit_form.orcid_id.data=content['author'][0][4]
            edit_form.researcher_id.data=content['author'][0][5]
            list_dep_author=dbase.get_dep_by_author(int(cur_page))
            edit_form.depat.data=list_dep_author[0][3]
            if len(list_dep_author) > 1:
                edit_form.depat_two.data=list_dep_author[1][3]
            else:
                edit_form.depat_two.data=NOT_DEP
            edit_form.list_lat_name.data=content['author'][0][6] 
        return content

    edit_form=forms.EditForm()    
    list_all_dep=dbase.get_nure_total_dep_list()
    edit_form.depat.choices=list_all_dep
    edit_form.depat_two.choices=list_all_dep
    content={}
    if cur_page != 0:
        content['author'] =dbase.get_author_by_id(int(cur_page))
    else:
        content=set_form_edit()

    if request.method == 'POST':
        if edit_form.submit_delete.data:
            # flash("Вы успешно удалили данные", "success")
            return redirect(url_for('.KhNURE'))
        elif edit_form.submit_escape.data:
            return redirect(request.url)

        if edit_form.validate_on_submit():
            if edit_form.submit_save.data:
                new_data =forms.EditStruct
                edit_form.populate_obj(new_data)
                if update_db_author(content,new_data,cur_page):
                    flash("Вы успешно обновили данные", "success")
                else:
                    flash("Ошибка обновления данных", "error")

            elif edit_form.submit_add.data:
                if  edit_form.one_lat_name.data:
                    if edit_form.list_lat_name.data:
                        edit_form.list_lat_name.data += '; '+ edit_form.one_lat_name.data
                    else:
                        edit_form.list_lat_name.data = edit_form.one_lat_name.data
                    edit_form.one_lat_name.data=''
                    flash("Вы добавили фамилию латиницы", "success")               
                else:
                    if edit_form.list_lat_name.data != content['author'][0][6]:
                        flash("Вы изменили список фамилий латиницы", "success")
                    else:
                        flash("Вы не добавили фамилию латиницы", "error")
        else:
            flash('Ошибка ввода данных', category = 'error')
    else:    
        set_form_edit(content)

    return render_template ('edit_author.j2', form = edit_form, content=content)


@app.route("/hnure",methods=['GET','POST'])
def KhNURE():   
    content = {} # словарь для передачи в шаблон    
    limit = PER_PAGE
        
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = 0 if page == 1 else (page-1) * limit    
    
    content['nure_dep'] = dbase.get_nure_total_dep_list()
    if request.method == 'GET':
        deportment=request.args.get("id_dep")
        fist_name=request.args.get("fist_name")
        if deportment and deportment.isnumeric():
                total_list = dbase.get_nure_one_dep_list(deportment)
                content['nure_current_dep']= dict(content['nure_dep'])[int(deportment)] 
        elif fist_name:
            total_list =dbase.get_nure_one_list(fist_name)
        else:
            total_list = dbase.get_nure_list()
            content['nure_current_dep']='Выбор кафедры ( ВСЕ )'
    else:
        total_list = dbase.get_nure_list()
        content['nure_current_dep']='Выбор кафедры ( ВСЕ )'
    
    if total_list:
        total = len(total_list)
        content['nure_list'] = total_list[offset:offset+limit]
    else:
        content['nure_list'] = 0
        total=0

    content['pagination'] = Pagination(page=page, total=total,outer_window=0,record_name='записей',   #search=False,
                                display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                                per_page=limit, bs_version=5)   #,alignment='right')
    
    content['title'] = 'Редактор списка сотрудников'

    return render_template('hnure.j2', content=content)


@app.route("/wos")
def WOS():
    return render_template('wos.j2')

@app.route("/scopus")
def Scopus():
    return render_template('scopus.j2')

@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == "__main__":
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
    app.run('192.168.1.110',debug=True)
    



