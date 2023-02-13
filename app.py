from flask import Flask, render_template, url_for, g, request, Blueprint

from flask_bootstrap import Bootstrap
from FDataBase import FDataBase 
import psycopg2
from flask_paginate import Pagination, get_page_parameter


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
    db = getattr(g, '_database',None)
    if db is None:
       db = g._database = connect_db()
    return db

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html',content = {'title':'Генератор отчетов'})


@app.route("/hnure",methods=['GET'])
#@app.route('/<section>/<int:cur_page>/', methods=['GET']
def KhNURE():   
    content = {} # словарь для передачи в шаблон
    db=get_db()
    dbase = FDataBase(db)
    total_list =dbase.get_nure_list()
    total = len(total_list)
    limit = PER_PAGE
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = 0 if page == 1 else (page-1) * limit    
    
    content['pagination'] = Pagination(page=page, total=total,outer_window=0,record_name='записей',   #search=False,
                                display_msg="Отображено <b>{start} - {end}</b> {record_name} из всего <b>{total}</b>", 
                                per_page=limit, bs_version=5)   #,alignment='right')
    content['nure_list'] = total_list[offset:offset+limit]
    content['title'] = 'Редактор списка сотрудников'

    return render_template('hnure.html', content=content)
       

@app.route("/wos")
def WOS():
    return render_template('wos.html')

@app.route("/scopus")
def Scopus():
    return render_template('scopus.html')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:  db.close()


if __name__ == "__main__":
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
    app.run('localhost',debug=True)
    



