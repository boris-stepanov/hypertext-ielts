#!virtualenv/bin/python

from json import dumps
from hashlib import md5
from string import ascii_letters, digits
import random
from yaml import load
# from config import Config
from source import db
from source.model.user import UserLogin
from source.model.exercise import Exercise, Task, Context, TaskGroup


if "choices" in dir(random):
    choices = random.choices
else:
    choices = lambda seq, k: [random.choice(seq) for i in range(k)]



def init():
    db.create_all()


def gen_students(input):
    output = open("students.csv", "a")
    for l in input:
        line = l.strip()
        print(line)
        if line[:2] == "__":
            group = line[2:]
            students.write("\n{}\n\n".format(group))
        elif line:
            login = "user_" + md5(line.encode('utf8')).hexdigest()[:8]
            password = ''.join(choices(ascii_letters + digits, k=8))
            db.session.add(UserLogin.init(login, group, password))
            students.output("{}\t{}\t{}\n".format(login, password, line))
    db.session.commit()


def gen_contexts(contexts):
    for context in contexts:
        items = list(context.items())[0]
        if isinstance(items[1][0], str):
            bs = bytes(dumps(items[1]), "utf8")
        else:
            merged = {}
            for i in items[1]:
                merged.update(i)
            bs = bytes(dumps(merged), "utf8")
        db.session.add(Context(term=items[0], content=bs))
    db.session.commit()


def gen_exercises(exercises):
    gid = 0
    for exercise in exercises:
        next = None
        groups = exercise['groups']
        groups.reverse()
        for group in groups:
            db.session.add(TaskGroup(next_group=next))
            gid += 1
            next = gid
            for task in group:
                db.session.add(Task.init(gid, task))
        db.session.add(Exercise(description_url=exercise['url'], start_task=next))
    db.session.commit()


if __name__ == "__main__":
    init()
    content = load(open("state.yaml"))
    db.session.add(UserLogin.init("guest", "anonymous", "guest"))
    gen_contexts(content["contexts"])
    gen_exercises(content["exercises"])
    db.session.commit()
    students = open("students.txt", "r")
