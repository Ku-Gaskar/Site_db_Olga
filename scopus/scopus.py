from flask import Blueprint, render_template, url_for, g, request,redirect,flash,current_app
from scopus.SC_Dbase import SC_Dbase


scopus=Blueprint('scopus',__name__,template_folder='templates',static_folder='static')
sc_dbase=None



@scopus.before_request
def before_request():
    global sc_dbase
    db=g.get('link_db') #current_app.config['DATABASE'])
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
    content['doc_sum']=sc_dbase.get_doc_sum()
    content['h_ind'] = sc_dbase.get_h_ind()

    return render_template('scopus/sc_index.html',content = content)

@scopus.route('/sc_report', methods=['GET', 'POST'])
def scopusReport():
    content={}
    
    return render_template('scopus/sc_report.html',content = content)# ,form = form)