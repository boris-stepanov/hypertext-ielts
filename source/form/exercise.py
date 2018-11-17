from source import db, log
from ..model.user import UserLogin
from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField
from wtforms.validators import InputRequired

class TaskForm(FlaskForm):
    task_id = IntegerField('task_id', validators=[InputRequired()])
    answer = TextAreaField('answer', validators=[InputRequired()])
