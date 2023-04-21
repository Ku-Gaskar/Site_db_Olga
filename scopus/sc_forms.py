from flask_wtf import FlaskForm
from wtforms import SearchField,IntegerField,SelectField,SelectMultipleField,SubmitField,BooleanField,RadioField
from wtforms.validators import NumberRange
from datetime import datetime
# from wtforms import widgets

# class CheckSelectMultipleField(SelectMultipleField):
#     widget=widgets.ListWidget(prefix_label=False)
#     option_widget=widgets.CheckboxInput()

class DataScForm:
    sc_search=None
    sc_buttons_search=None
    sc_radio_auth_atcl=None
    sc_select_dep=None
    sc_select_year=None
    sc_article=None
    sc_book=None
    sc_conf=None
    sc_other=None
    sc_bool_limit=None
    sc_input_limit=None
    sc_buttons_cancel=None
    sc_buttons_ok=None
    sc_rep_article=None
    sc_rep_authors=None
    sc_rep_sum=None
    sc_rep_authors_with_stat=None





    
class SC_Form(FlaskForm):

    sc_search=SearchField(description='Поиск')
    sc_buttons_search=SubmitField('Поиск')
    sc_radio_auth_atcl=RadioField(choices=[('author','Поиск по авторам'),('article','Поиск по статьям')], default='author')
    sc_select_dep=SelectField('Кафедра',default=9999) 
    sc_select_year=SelectMultipleField('Год',choices = [('Все')] + [(str(year_)) for year_ in range(datetime.now().year,1962,-1)], default=['Все'])
    sc_article=BooleanField('Статьи',default=True)
    sc_book=BooleanField('Книги',default=True)
    sc_conf=BooleanField('Конференции',default=True)
    sc_other=BooleanField('Другие ...',default=True)
    sc_bool_limit=BooleanField('Лимит на кол-во статей',default=False)
    sc_input_limit=IntegerField('Не менее статей автора:',validators=[NumberRange(min=0,max=99)],default=0)
    sc_buttons_cancel=SubmitField('Сбросить')
    sc_buttons_ok=SubmitField('Применить')

    sc_rep_article=SubmitField('Публикации с авторами (с учетом фильтра)')
    sc_rep_authors_with_stat = SubmitField('Авторы + Док. + Цит. + H_инд. (с учетом фильтра)')
    sc_rep_authors=SubmitField('Авторы со статьями (с учетом фильтра)')
    sc_rep_sum=SubmitField('Cумма цитирований авторов по кафедрам (без учета фильтра)')
