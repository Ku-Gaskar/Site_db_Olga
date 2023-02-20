from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField,SubmitField,IntegerField
from wtforms.validators import Email, DataRequired, EqualTo,InputRequired,Optional,Regexp,Length
from FDataBase import FDataBase

# class LoginForm(Form):
#     email = StringField('E-mail', validators=[Email(), DataRequired()])
#     password = PasswordField('Пароль', validators=[DataRequired()])

# class RegistrationForm(LoginForm):
#     password_repeat = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])


class EditForm(FlaskForm):
    name_author=StringField('ФИО',validators=[DataRequired()])
    scopus_id=StringField('Scopus_ID')#,validators=[Optional(),Regexp(r'[0-9]{8-12}',message='Не соответствует формату')])#,Length(min=8, max=12, message="Scopus_ID должен быть от 8 до 12 цифр")]) #Regexp('[0-9]{9-12}')])
    orcid_id=StringField('Orcid_ID',validators=[Optional(),Regexp('[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}',
                                                                            message='Формат: XXXX-XXXX-XXXX-XXXX')])
    researcher_id=StringField('Researcher_ID',validators=[Optional(),Regexp('[A-Za-z]{1,}-[0-9]{3,}-[0-9]{4}',
                                                                            message='Формат: A(AAA)-XXX(XXX)-XXXX')])
    depat=SelectField('Кафедра',coerce=int)
    
    list_lat_name=TextAreaField("ФИО латиница",render_kw={'class': 'form-control', 'rows': 3})
    one_lat_name=StringField(render_kw={'class': 'form-control'})
    
    submit_escape = SubmitField("Отмена")
    submit_add = SubmitField("Добавить")
    submit_save = SubmitField("Сохранить изменения")
