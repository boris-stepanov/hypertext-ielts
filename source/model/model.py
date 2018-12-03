from typing import List, Dict, Optional, Type
from datetime import datetime
from bcrypt import hashpw, gensalt
from flask import flash
from source import db, log, lm


# Users


class AnonymousUserLogin:
    """
    Login for guest users
    """

    is_authenticated: bool = False
    is_active: bool = False
    is_anonymous: bool = True

    group: str = "anonymous"
    tries: Dict[int, int] = {}

    @staticmethod
    def get_id() -> None:
        return None

    def add_try(self, tr: "Try") -> None:
        self.tries[tr.eid] = tr.id

    def get_try(self, eid: int) -> Optional["Try"]:
        record = self.tries.get(eid)
        if not record:
            return None
        tr = Try.query.get(record)
        if tr.finished_at is not None:
            return None
        return tr

    def get_tries(self) -> List["Try"]:
        res: List["Try"] = []
        for i in self.tries.values():
            res.append(Try.query.get(i))
        return res

    def __repr__(self):
        return "<AnonymousUser(tries={})>".format(self.tries)


class UserLogin(db.Model):
    """
    Common user class with additional student's group attribute
    """
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
    def init(cls, login: str, group: str, password: str) -> "UserLogin":
        """
        Safe User constructor, performs hashing of the password
        Doesn't commit new user into the database
        """
        user = cls(login=login, group=group, hash="")
        user.update_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_password(self, password):
        log("User {} changes the password".format(self.login))
        self.hash = hashpw(bytes(password, "utf8"), gensalt())
        db.session.commit()

    def check_password(self, password: str) -> bool:
        """
        Compare stored hash with hash of input password
        """
        return hashpw(bytes(password, "utf8"), self.hash) == self.hash

    @classmethod
    def get(cls: Type["UserLogin"], uid: int) -> Optional["UserLogin"]:
        """
        Get User by user_id
        """
        return cls.query.get(uid)

    def get_try(self, eid: int) -> Optional["Try"]:
        """
        Check if user is doing exercise now
        """
        for i in self.tries:
            if i.eid == eid and i.finished_at is None:
                return i
        return None

    def get_tries(self) -> List["Try"]:
        return self.tries

    def add_try(self, tr: "Try") -> None:
        pass

    def get_id(self) -> str:
        """
        Necessary method for flask_login
        """
        return str(self.id)

    def __repr__(self):
        return "<User(id='{}', group='{}', active={})>".format(
            self.id, self.group, self.in_action())


lm.anonymous_user = AnonymousUserLogin

@lm.user_loader
def load_user(uid: str) -> Optional[UserLogin]:
    """
    Necessary Flask_login callback
    """
    return UserLogin.get(int(uid))


# Exercises


tags = db.Table('tags',
                db.Column('task_id',
                          db.Integer,
                          db.ForeignKey('tasks.id'),
                          primary_key=True),
                db.Column('context_term',
                          db.Integer,
                          db.ForeignKey('contexts.id'),
                          primary_key=True))


class Try(db.Model):
    __tablename__ = "tries"
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    eid = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    step = db.Column(db.Integer, db.ForeignKey('groups.id'))

    @classmethod
    def init(cls, user, exercise):
        # type: (Any["AnonymousUserLogin", "UserLogin"], "Exercise") -> "Try"
        uid = user.get_id()
        if uid:
            log("User {} starts the exercise {}".format(user.id, exercise.id))
        else:
            log("Anonymous starts the exercise {}".format(exercise.id))
        new_try = cls(result=0,
                      text="",
                      started_at=datetime.now(),
                      finished_at=None,
                      uid=uid,
                      eid=exercise.id,
                      step=exercise.start_task)
        db.session.add(new_try)
        db.session.commit()
        user.add_try(new_try)
        return new_try

    def append(self, sentence: str) -> None:
        self.text = " ".join([self.text, sentence])
        db.session.commit()

    def inc_fault(self) -> None:
        self.result += 1
        db.session.commit()

    def next(self) -> bool:
        """
        Update stage of the current try
        Return True if uses finished exercise
        """
        self.step = self.groups.next_group
        if self.step:
            flash("Правильно!", "success")
            db.session.commit()
            return False
        flash("Упражнение завершено.", "success")
        self.finish(True)
        return True

    def finish(self: "Try", success: bool) -> None:
        fin_type = "finished" if success else "cancelled"
        if self.uid:
            u_type = "User {}".format(self.uid)
        else:
            u_type = "Anonymous"
        log("{} {} the exercise {}".format(u_type, fin_type, self.eid))
        self.finished_at = datetime.now()
        if not success:
            self.result = -1
        if self.users:
            db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Try(id={}, user={}, exercise={}, step={})>".format(
            self.id, self.uid, self.eid, self.step)


class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description_url = db.Column(db.Text)
    start_task = db.Column(db.Integer, db.ForeignKey('groups.id'))
    tries = db.relationship('Try', backref='exercises', lazy=True)

    def __repr__(self):
        return "<Exercise(id={}, start_task={})>".format(
            self.id, self.start_task)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    formulae = db.Column(db.Text, nullable=False)
    contexts = db.relationship('Context',
                               secondary=tags,
                               lazy='subquery',
                               backref=db.backref('tasks', lazy=True))

    @classmethod
    def init(cls, group_id: int, formulae: str) -> "Task":
        task = cls(group_id=group_id, formulae=formulae)
        split = formulae.strip().split('$')
        res = set()
        for i, term in enumerate(split):
            if i % 2 == 1:
                res.add(Context.query.filter_by(term=term).first())
        task.contexts = list(res)
        db.session.add(task)
        db.session.commit()
        return task

    def __repr__(self):
        return "<Task(id={}, group_id={}, formulae='{}')>".format(
            self.id, self.group_id, self.formulae)


class TaskGroup(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    next_group = db.Column(db.Integer,
                           db.ForeignKey('groups.id'),
                           nullable=True)
    exercises = db.relationship('Exercise', backref='groups', lazy=True)
    tasks = db.relationship('Task', backref='groups', lazy=True)
    tries = db.relationship('Try', backref='groups', lazy=True)

    def __repr__(self):
        return "<Group(id={}, next_group={})>".format(self.id, self.next_group)


class Context(db.Model):
    __tablename__ = "contexts"
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(80), index=True, unique=True, nullable=False)
    content = db.Column(db.LargeBinary)

    def __repr__(self):
        return "<Context(id={}, term='{}', content='{}')>".format(
            self.id, self.term, self.content)
