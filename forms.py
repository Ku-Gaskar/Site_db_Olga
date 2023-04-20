from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField,SubmitField,IntegerField,SelectMultipleField,BooleanField 
from wtforms.validators import Email, DataRequired, EqualTo,InputRequired,Optional,Regexp,Length


# class LoginForm(Form):
#     email = StringField('E-mail', validators=[Email(), DataRequired()])
#     password = PasswordField('Пароль', validators=[DataRequired()])

# class RegistrationForm(LoginForm):
#     password_repeat = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])

class EditStruct:
    name_author=None
    scopus_id   = None
    scopus_id_1 = None
    scopus_id_2 = None
    orcid_id   = None
    orcid_id_1 = None
    orcid_id_2 = None
    researcher_id   = None
    researcher_id_1 = None
    researcher_id_2 = None
    googlescholar_id = None
    googlescholar_id_1 = None
    googlescholar_id_2 = None
    depat=None
    list_lat_name=None
    one_lat_name=None
    part_time_worker=None
    depat_two=None
    submit_escape = None
    submit_add = None
    submit_save = None
    submit_delete= None



class EditForm(FlaskForm):
    name_author=StringField('ФИО',validators=[DataRequired()])
 
    scopus_id   = StringField('Scopus_ID',validators=[Optional(),Regexp('^[\d]{8,12}$',message='Scopus_ID должен быть от 8 до 12 цифр')]) #Regexp('[0-9]{9-12}')])
    scopus_id_1 = StringField('Scopus_ID_1',validators=[Optional(),Regexp('^[\d]{8,12}$',message='Scopus_ID должен быть от 8 до 12 цифр')]) #Regexp('[0-9]{9-12}')])
    scopus_id_2 = StringField('Scopus_ID_1',validators=[Optional(),Regexp('^[\d]{8,12}$',message='Scopus_ID должен быть от 8 до 12 цифр')]) #Regexp('[0-9]{9-12}')])
 
    orcid_id   = StringField('Orcid_ID',validators=[Optional(),Regexp('^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}$',message='Формат: XXXX-XXXX-XXXX-XXXX')])
    orcid_id_1 = StringField('Orcid_ID',validators=[Optional(),Regexp('^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}$',message='Формат: XXXX-XXXX-XXXX-XXXX')])
    orcid_id_2 = StringField('Orcid_ID',validators=[Optional(),Regexp('^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}$',message='Формат: XXXX-XXXX-XXXX-XXXX')])
 
    researcher_id   = StringField('Researcher_ID',validators=[Optional(),Regexp('^[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}$',message='Формат: A(AAA)-XXX(XXX)-XXXX')])#,Length(min=10, max=16)])
    researcher_id_1 = StringField('Researcher_ID',validators=[Optional(),Regexp('^[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}$',message='Формат: A(AAA)-XXX(XXX)-XXXX')])#,Length(min=10, max=16)])
    researcher_id_2 = StringField('Researcher_ID',validators=[Optional(),Regexp('^[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}$',message='Формат: A(AAA)-XXX(XXX)-XXXX')])#,Length(min=10, max=16)])

    googlescholar_id   = StringField('Googlescholar',validators=[Optional(),Length(min=12, max=12)])
    googlescholar_id_1 = StringField('Googlescholar') #,validators=[Optional(),Regexp('^[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}$',message='Формат: A(AAA)-XXX(XXX)-XXXX')])#,Length(min=10, max=16)])
    googlescholar_id_2 = StringField('Googlescholar') #,validators=[Optional(),Regexp('^[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}$',message='Формат: A(AAA)-XXX(XXX)-XXXX')])#,Length(min=10, max=16)])
    
    depat=SelectField('Кафедра',coerce= int)
    
    list_lat_name=TextAreaField("ФИО латиница",render_kw={'class': 'form-control', 'rows': 3})
    one_lat_name=StringField(render_kw={'class': 'form-control'})
    
    part_time_worker=BooleanField("Совместитель")
    depat_two=SelectField('Кафедра 2',coerce= int,default=10000)

    submit_escape = SubmitField("Отмена/Обновить")
    submit_add = SubmitField("Добавить")
    submit_save = SubmitField("Сохранить изменения")
    submit_delete=SubmitField("Удалить")

class LoginForm(FlaskForm):
      username=StringField('Логин', validators=[DataRequired()])
      password = PasswordField('Пароль', validators=[DataRequired()])
      submit=SubmitField("Войти")