from flask import Flask, render_template, url_for, g, request, Blueprint,redirect,flash

from flask_bootstrap import Bootstrap
from FDataBase import FDataBase, Author
import psycopg2
from flask_paginate import Pagination, get_page_parameter
import forms


DATABASE='localhost'
PORT = '5432'
DEBUG=True
SECRET_KEY='trwyuwteutweur376437643764kjf'

PER_PAGE=100     # записей на одной странице nure
 

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
def delete(cur_page):

    edit_form=forms.EditForm()    
    edit_form.depat.choices=dbase.get_nure_total_dep_list()

    if request.method == 'POST':
        if edit_form.validate_on_submit():
            flash("Вы успешно обновили данные", "success")
            print('Delete')
            return redirect(request.url)
        else:
            flash('Ошибка ввода данных', category = 'error')
            return redirect(request.url)
    else:    
        content={}
        content['author'] =dbase.get_author_by_id(int(cur_page))
        edit_form.name_author.data=content['author'][0][1]
        edit_form.scopus_id.data=content['author'][0][3]
        edit_form.orcid_id.data=content['author'][0][4]
        edit_form.researcher_id.data=content['author'][0][5]
        edit_form.depat.data=dbase.get_dep_by_author(int(cur_page))[0][3]
        return render_template ('delete.j2', form = edit_form, content=content)
    
    # content['cur_dep']=dbase.get_dep_by_author(int(cur_page))
    
    


# @app.route("/hnure/<int:cur_page>",methods=['GET','POST']) 
# def hnure(cur_page):
#     if request.method == 'POST':
#         print(cur_page)
#     content={}
#     content['author'] =dbase.get_author_by_id(int(cur_page))
#     content['cur_dep']=dbase.get_dep_by_author(int(cur_page))
#     content['nure_dep'] = dbase.get_nure_total_dep_list()
#     return render_template('edit_author.j2', content=content)


@app.route("/hnure",methods=['GET','POST'])
def KhNURE():   
    content = {} # словарь для передачи в шаблон    
    limit = PER_PAGE
        
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = 0 if page == 1 else (page-1) * limit    
    
    content['nure_dep'] = dbase.get_nure_total_dep_list()
    if request.method == 'POST':
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
    



