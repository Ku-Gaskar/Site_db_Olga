from flask import render_template, url_for, g, request, redirect,flash,abort

# from flask_bootstrap import Bootstrap
# import psycopg2
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_user,login_required,logout_user, current_user
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash , check_password_hash 

from FDataBase import FDataBase
import forms

import app_logger

from gevent.pywsgi import WSGIServer


# DATABASE='localhost'
# PORT = '5432'
DEBUG=False

PER_PAGE=100     # записей на одной странице nure
NOT_DEP=10000    # id кафедры которой нет

#************** изменения в коде (перенос в init_app ) **********************
from init_app import create_app,login_manager, dbase, get_db
# from init_app import socketio

# from flask import Flask
# from flask_login import LoginManager
# from scopus.scopus import scopus
# from wos.wos import wos
# SECRET_KEY='fa85ab790e11c98bc7b81685ea4a29992f20b45a'
# app = Flask(__name__)
# app.config.from_object(__name__)

# login_manager=LoginManager(app)
# login_manager.login_view='login'
# login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
# login_manager.login_message_category = "success"

# app.register_blueprint(scopus,url_prefix="/scopus")
# app.register_blueprint(wos,url_prefix="/wos")
#-------------------------------------------------------------------------------
# dbase:FDataBase = None

app = create_app(True)

# def connect_db():
#     conn = psycopg2.connect( host=DATABASE, port=PORT, user="postgres", password="postgress")
#     return conn

# def get_db():
#     '''Соединение с БД, если оно еще не установлено'''
#     if not hasattr(g, 'link_db'):
#         g.link_db = connect_db()
#     return g.link_db

def update_db_author(cont,d:forms.EditStruct,id):
    a,c = True, True 
    if id == 0:
        id=dbase.insert_new_author(d)
        if not id: return False
        cont['author'] =dbase.get_author_by_id(id)
    # удаление автора -----------
    
    # обработка кафедр ----------
    a=dbase.delete_dep_by_id_author(id)
    a=dbase.insert_dep_by_id_author(id,cont['author'][0][1],d.depat)

    if d.part_time_worker:
        a=dbase.insert_dep_by_id_author(id,cont['author'][0][1],d.depat_two)
        # return True if a else False

    # обработка scopus_id
    db_list_scopus=dbase.get_table_author_in_scopus_by_id_author(id)
    dbase.delete_scopus_id_by_author_id(id)
    if db_list_scopus:
        for row in db_list_scopus:
            if d.scopus_id and (d.scopus_id == row[1]):
                dbase.insert_scopus_id_struct(row)
            elif d.scopus_id_1 and (d.scopus_id_1 == row[1]):
                dbase.insert_scopus_id_struct(row)
            elif d.scopus_id_2 and (d.scopus_id_2 == row[1]):
                dbase.insert_scopus_id_struct(row)
            else:
                row=list(row)
                row[1]=d.scopus_id
                dbase.insert_scopus_id_struct(row)
                
    dbase.insert_scopus_id_by_author_id(id,d)
                                          
    if (cont['author'][0][1] != d.name_author) or (cont['author'][0][4] != d.orcid_id
        ) or (cont['author'][0][5] != d.researcher_id) or (cont['author'][0][7] != d.googlescholar_id):
        b=dbase.update_name_orcid_reasearcher_id_by_author_id(d,cont)
    if cont['author'][0][6]!= d.list_lat_name:
        dbase.delete_lat_name_by_id_author(id)
        name_lat_dict = {}
        for lat_name in d.list_lat_name.split(';'):
            name_lat_dict[lat_name.strip()] = id
        for key,id_name in name_lat_dict.items():
            c=dbase.insert_lat_name_by_author_id(key,id_name)

    return True if a and c else False 


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id,dbase)


@app.route('/login', methods=['POST','GET'])
def login():
    form=forms.LoginForm()
    if form.validate_on_submit():
        user=dbase.getUserByName(request.form['username'])
        if user and check_password_hash(user['psw'],request.form['password']):
            userLogin=UserLogin().create(user)
            login_user(userLogin)
            return redirect(request.args.get("next") or url_for('.KhNURE')) 
        flash('Пароль не верный','error')
    return render_template('login.j2',form=form,content = {'title':'Вход в систему'})    


@app.before_request
def before_request():
    global dbase
    dbase = FDataBase(get_db())


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.j2',content = {'title':'Генератор отчетов'})


@app.route("/hnure/<int:cur_page>",methods=['GET','POST'])
@login_required 
def edit_author(cur_page):
    def set_form_edit(content:dict={'author':[(None,'','','','','','','')]}):
        if (cur_page!=0):
            edit_form.name_author.data=content['author'][0][1]
            if content['author'][0][3]:
                list_sc= content['author'][0][3].split(';')
                edit_form.scopus_id.data=list_sc[0]
                if len(list_sc) >1 :edit_form.scopus_id_1.data=list_sc[1]
                if len(list_sc) >2 :edit_form.scopus_id_2.data=list_sc[2]
            edit_form.orcid_id.data=content['author'][0][4]
            edit_form.researcher_id.data=content['author'][0][5]
            list_dep_author=dbase.get_dep_by_author(int(cur_page))
            edit_form.depat.data=list_dep_author[0][3]
            if len(list_dep_author) > 1:
                edit_form.depat_two.data=list_dep_author[1][3]
            else:
                edit_form.depat_two.data=NOT_DEP
            edit_form.list_lat_name.data=content['author'][0][6]
            edit_form.googlescholar_id.data=content['author'][0][7] 
        return content

    if current_user.get_id() != '1':
        flash('Авторизуйтесь как admin','error')
        return  redirect(url_for('login',next=request.full_path))
    
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
            a=dbase.hiden_author_by_id(cur_page)
            if a:
                flash("Вы успешно удалили "+ content['author'][0][1], "success")
            else:
                flash("Не удалось удалить "+ content['author'][0][1], "error")
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
@login_required
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

    content['pagination'] = Pagination(page=page, total=total,outer_window=0,record_name='записей',
                                display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                                per_page=limit, bs_version=5)    
    content['title'] = 'Редактор списка сотрудников'
    return render_template('hnure.j2', content=content)

@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()

def my_split(content:str) -> list[str]:
    """Создание пользовательского фильтра для jinja """       
    return content.split(';') if content else []  

@app.route("/logout") # нет перехода на этот маршрут
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))   

if __name__ == "__main__":
   logger = app_logger.get_logger(__name__)
   logger.info("Программа стартует") 
 
   app.jinja_env.filters['my_split'] = my_split
#    app.run('192.168.1.102', debug = DEBUG) 
   http_server = WSGIServer(('192.168.1.102',5000), app)
   http_server.serve_forever()
#    socketio.run(app, host='192.168.1.102', port=5000, debug=True) 
    
    


