from flask import flash
from datetime import datetime
from source import db, log


tags = db.Table('tags',
                db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
                db.Column('context_term', db.Integer, db.ForeignKey('contexts.id'), primary_key=True))


class Try(db.Model):
    __tablename__ = "tries"
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eid = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    step = db.Column(db.Integer, db.ForeignKey('groups.id'))

    @classmethod
    def init(cls, user, exercise):
        log("User {} starts the exercise {}".format(user.id, exercise.id))
        new_try = cls(result=0, text="", started_at=None, finished_at=None, uid=user.id, eid=exercise.id, step=exercise.start_task)
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

    def next(self):
        self.step = self.groups.next_group
        if not self.step:
            flash("Упражнение завершено.", "success")
            self.finish(True)
        else:
            flash("Правильно!", "success")
        db.session.commit()

    def finish(self, success):
        log("User {} finishes the exercise {}".format(self.uid, self.eid))
        self.finished_at = datetime.now()
        if not success:
            self.result = -1
        db.session.commit()

    def __repr__(self):
        return "<Try(id={}, user={}, exercise={}, step={})>".format(self.id, self.uid, self.eid, self.step)


class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description_url = db.Column(db.Text)
    start_task = db.Column(db.Integer, db.ForeignKey('groups.id'))
    tries = db.relationship('Try', backref='exercises', lazy=True)

    def __repr__(self):
        return "<Exercise(id={}, start_task={})>".format(self.id, self.start_task)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    formulae = db.Column(db.Text, nullable=False)
    contexts = db.relationship('Context', secondary=tags, lazy='subquery', backref=db.backref('tasks', lazy=True))

    @classmethod
    def init(cls, group_id, formulae):
        task = cls(group_id=group_id, formulae=formulae)
        split = formulae.strip().split('$')
        res = set()
        for i in range(len(split)):
            if i % 2 == 1:
                res.add(Context.query.filter_by(term=split[i]).first())
        task.contexts = list(res)
        return task

    def __repr__(self):
        return "<Task(id={}, group_id={}, formulae='{}')>".format(self.id, self.group_id, self.formulae)


class TaskGroup(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    next_group = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
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
        return "<Context(id={}, term='{}', content='{}')>".format(self.id, self.term, self.content)
