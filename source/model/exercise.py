from flask import flash
from datetime import datetime
from source import db


tags = db.Table('tags',
                db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
                db.Column('context_id', db.Integer, db.ForeignKey('contexts.term'), primary_key=True))


class Try(db.Model):
    __tablename__ = "tries"
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, index=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eid = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    step = db.Column(db.Integer, db.ForeignKey('tasks.group_id'))

    def __init__(self, user, exercise):
        self.uid = user.id
        self.eid = exercise.id
        self.text = ""
        self.step = exercise.start_task
        self.result = 0

    @classmethod
    def init_try(cls, user, exercise):
        new_try = cls(user, exercise)
        db.session.add(new_try)
        db.session.commit()
        return new_try

    def append(self, sentence):
        self.text = " ".join([self.text, sentence])
        db.session.commit()

    def start(self):
        self.started_at = datetime.now()
        db.session.commit()

    def inc_fault(self):
        self.result += 1
        db.session.commit()

    def next(self, task_id):
        self.step = Task.query.get(task_id).next_task
        if not self.step:
            flash("Упражнение завершено.", "success")
            self.finish(True)
        else:
            flash("Правильно!", "success")
        db.session.commit()

    def finish(self, success):
        self.finished_at = datetime.now()
        if not success:
            self.result = -1
        db.session.commit()

    def __repr__(self):
        return "<Try {}, user {}, exercise {}, step {}>".format(self.id,
                                                                self.uid,
                                                                self.eid,
                                                                self.step)


class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, index=True, primary_key=True)
    description_url = db.Column(db.Text)
    start_task = db.Column(db.Integer, db.ForeignKey('tasks.group_id'))
    tries = db.relationship('Try', backref='exercises', lazy=True)

    def __init__(self, description, group_id):
        self.description = description
        self.start_task = group_id

    def __repr__(self):
        return "<Exercise {}, first task {}>".format(self.id, self.start_task)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, index=True, primary_key=True)
    group_id = db.Column(db.Integer, index=True)
    formulae = db.Column(db.Text, nullable=False)
    next_task = db.Column(db.Integer, db.ForeignKey('tasks.group_id'))
    users = db.relationship('Try', backref='tasks', lazy=True)
    contexts = db.relationship('Context', secondary=tags, lazy='subquery', backref=db.backref('tasks', lazy=True))

    def __init__(self, group_id, formulae, next_task):
        self.group_id = group_id
        self.formulae = formulae
        self.next_task = next_task

    def parse_formulae(self):
        split = self.formulae.strip().split('$')
        res = set()
        for i in range(len(split)):
            if i % 2 == 1:
                res.add(Context.query.get(split[i]))
        self.contexts = list(res)
        db.session.commit()

    def __repr__(self):
        return "<Task {}, eid {}, next_task {}>".format(self.id,
                                                        self.group_id,
                                                        self.next_task)


class Context(db.Model):
    __tablename__ = "contexts"
    term = db.Column(db.String(80), unique=True, primary_key=True, index=True, nullable=False)
    content = db.Column(db.LargeBinary)

    def __init__(self, name, content):
        self.term = name
        self.content = content

    def __repr__(self):
        return "<Context {}>".format(self.term)
