from datetime import datetime, timedelta
from bcrypt import hashpw, gensalt
from .. import lm, db


@lm.user_loader
def load_user(userid):
    return UserLogin.query.get(int(userid))

class UserLogin(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, index=True, nullable=False)
    group = db.Column(db.String(80))
    hash = db.Column(db.String(60), nullable=False)
    tries = db.relationship('Try', backref='users', lazy=True)

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def __init__(self, login, group, password):
        self.login = login
        self.group = group
        self.this_try = None
        self.update_password(password)

    def check_password(self, password):
        return hashpw(bytes(password, "utf8"), self.hash) == self.hash

    def update_password(self, password):
        self.hash = hashpw(bytes(password, "utf8"), gensalt())
        db.session.commit()

    @classmethod
    def get(cls, uid):
        return cls.user_database.get(uid)

    def in_action(self):
        return self.tries and self.tries[-1].finished_at is None

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return "<User {}, group {}>".format(self.id, self.group)
