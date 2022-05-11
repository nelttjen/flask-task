from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    team_leader = IntegerField('Лидер команды', validators=[DataRequired()])
    job = StringField('Описание работы', validators=[DataRequired()])
    work_size = IntegerField('Время на работу', validators=[DataRequired()])
    collaborators = StringField('Участники (id участников через ", ")')
    hazard = IntegerField('Hazard level', validators=[DataRequired()])
    finished = BooleanField('Работа окончена?', default=False)
    submit = SubmitField('Сохранить')