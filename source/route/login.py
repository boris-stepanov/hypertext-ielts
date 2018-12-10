from flask import render_template, redirect, g, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from source import source
from ..form.login import LoginForm


@source.route('/', methods=['GET', 'POST'])
@source.route('/login', methods=['GET', 'POST'])
def login():
    """
    Simple login page
    """
    if g.login.is_authenticated:
        return redirect(url_for('texts'))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.check_login()
        if not user:
            flash("Unknown login/password combination", "error")
            return render_template('login.html', form=form)
        session['login'] = form.login.data
        login_user(user)
        return redirect(url_for('texts'))
    return render_template('login.html', form=form)


@source.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    Simple logout
    """
    logout_user()
    return redirect(url_for('login'))
