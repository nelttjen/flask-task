from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired


class FileForm(FlaskForm):
    file = FileField('Загрузите файл', validators=[DataRequired()])
    submit = SubmitField('Submit')