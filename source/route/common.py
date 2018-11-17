from datetime import datetime
from flask import render_template, g, redirect, url_for
from .. import db, source
from flask_login import current_user
from functools import wraps


def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("/login"))
        return f(*args, **kwargs)
    return func

@source.before_request
def before_request():
    g.login = current_user
    if g.login.is_authenticated:
        g.user = current_user
        g.login.last_seen = datetime.now()
        db.session.add(g.login)
        db.session.commit()


@source.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@source.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
