from flask import render_template, redirect, request, g, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from source import source
from ..form.login import LoginForm, ChangePasswordForm


@source.route('/', methods=['GET', 'POST'])
@source.route('/login', methods=['GET', 'POST'])
def login():
    if g.login.is_authenticated:
        return redirect(url_for('exercise'))
    form = LoginForm()
    if form.validate_on_submit():
        if request.form['action'] == "Login":
            user = form.check_login()
            if not user:
                flash("Unknown login/password combination", "error")
                return render_template('login.html', form=form)
            session['login'] = form.login.data
            login_user(user)
            g.user = user
            return redirect(url_for('exercise'))
    return render_template('login.html', form=form)


#@source.route('/profile', methods=['GET', 'POST'])
#@login_required
#def profile():
#    form = ChangePasswordForm()
#    if request.method == 'POST':
#        if form.validate_on_submit(g.user):
#            g.user.update_password(form.new.data)
#            logout_user()
#            return redirect(url_for('login'))
#    return render_template('profile.html', form=form)


@source.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
