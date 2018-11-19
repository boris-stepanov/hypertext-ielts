from bcrypt import hashpw, gensalt
from source import lm, db, log


@lm.user_loader
def load_user(userid):
    return UserLogin.query.get(int(userid))


class UserLogin(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, index=True, nullable=False)
    group = db.Column(db.String(80))
    hash = db.Column(db.Binary(60), nullable=False)
    tries = db.relationship('Try', backref='users', lazy=True)

    is_authenticated = True
    is_active = True
    is_anonymous = False

    @classmethod
    def init(cls, login, group, password):
        user = cls(login=login, group=group, hash="")
        user.update_password(password)
        return user

    def check_password(self, password):
        return hashpw(bytes(password, "utf8"), self.hash) == self.hash

    def update_password(self, password):
        log("User {} changes the password".format(self.login))
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
        return "<User(id='{}', group='{}', active={})>".format(self.id, self.group, self.in_action())
