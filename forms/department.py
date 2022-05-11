from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class DepForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    chief = IntegerField('Chief_id', validators=[DataRequired()])
    members = StringField('Members')
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')