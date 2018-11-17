from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Regexp, Length
from ..model.user import UserLogin

LOGIN_REGEX = Regexp(r'^[\w\-\_]{3,20}$')


class LoginForm(FlaskForm):
    login = StringField('login', validators=[LOGIN_REGEX])
    password = PasswordField('password', validators=[Length(min=1, max=30)])

    def check_login(self):
        user = UserLogin.query.filter_by(login=self.login.data).first()
        if user is None or not user.check_password(self.password.data):
            self.login.errors.append('Unknown login/password combination')
            return None
        return user


class ChangePasswordForm(FlaskForm):
    current = PasswordField('password', validators=[Length(min=1, max=30)])
    new = PasswordField('password', validators=[Length(min=8, max=30)])
    repeat = PasswordField('password', validators=[Length(min=8, max=30)])

    def validate_on_submit(self, user):
        if FlaskForm.validate_on_submit(self):
            if user.check_password(self.current.data):
                if self.new.data== self.repeat.data:
                    return True
                else:
                    flash("Введённые пароли не совпадают", "error")
            else:
                flash("Введённый пароль не верен", "error")
        else:
            flash("Пароль должен иметь длину от 8 до 30 символов", "error")
        return False


class HiddenForm(FlaskForm):
    pass
