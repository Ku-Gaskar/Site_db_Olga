from flask import Flask,g
# from flask_socketio import SocketIO
# import os
from flask_login import LoginManager
import psycopg2
from FDataBase import FDataBase

# --------------- constants ---------------------------- 
DATABASE='localhost'
PORT = '5432'
DEBUG=True
SECRET_KEY='fa85ab790e11c98bc7b81685ea4a29992f20b45a'

PER_PAGE=100     # записей на одной странице nure
NOT_DEP=10000    # id кафедры которой нет

#---------------------------------------------------------

# socketio:SocketIO = SocketIO()
login_manager = LoginManager()

dbase:FDataBase = None

def create_app(debug=False):
    
    
    app = Flask(__name__)
    # app.debug = debug
    app.config.from_object(__name__)
    
    app.config['SECRET_KEY'] = SECRET_KEY
    
    from scopus.scopus import scopus
    from wos.wos import wos
    
    login_manager.init_app(app)
    login_manager.login_view='login'
    login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
    login_manager.login_message_category = "success"

    app.register_blueprint(scopus,url_prefix="/scopus")
    app.register_blueprint(wos,url_prefix="/wos")
    # os.environ['GEVENT_SUPPORT'] = 'True'    
    # socketio.init_app(app)  
    return app


def connect_db():
    conn = psycopg2.connect( host=DATABASE, port=PORT, user="postgres", password="postgress")
    return conn

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# app = Flask(__name__)
