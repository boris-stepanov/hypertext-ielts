#!virtualenv/bin/python

from json import dumps
from hashlib import md5
from string import ascii_letters, digits
from random import choices
from yaml import load
from config import Config
from source import db
from source.model.user import UserLogin
from source.model.exercise import Exercise, Task, Context


content = load(open("state.yaml"))

db.create_all()

db.session.add(UserLogin("root", "", "redhothotie"))
students = open("students.csv", "w")
for l in open("students.txt"):
    line = l.strip()
    print(line)
    if line[:2] == "__":
        group = line[2:]
        students.write("{}\n\n".format(group))
    elif line:
        login = "user_" + md5(line.encode('utf8')).hexdigest()[:8]
        password = ''.join(choices(ascii_letters + digits, k=8))
        db.session.add(UserLogin(login, group, password))
        students.write("{}\t{}\t{}\n".format(login, password, line))
db.session.commit()

for context in content['contexts']:
    items = list(context.items())[0]
    if isinstance(items[1][0], str):
        bs = bytes(dumps(items[1]), "utf8")
    else:
        merged = {}
        for i in items[1]:
            merged.update(i)
        bs = bytes(dumps(merged), "utf8")
    db.session.add(Context(items[0], bs))
db.session.commit()

counter = 1
for exercise in content['exercises']:
    db.session.add(Exercise(exercise['url'], counter))
    groups = exercise['groups']
    limit = counter + len(groups) - 1
    for group in groups:
        if counter == limit:
            next = None
        else:
            next = counter + 1
        for task in group:
            item = Task(counter, task, next)
            db.session.add(item)
            db.session.commit()
            item.parse_formulae()
            db.session.commit()
        counter += 1
db.session.commit()
