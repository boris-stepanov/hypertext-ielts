from functools import reduce
from json import loads
from flask_login import login_required
from flask import render_template, redirect, request, g, url_for, flash
from .. import source, check_answer
from ..model.exercise import Exercise, Try, Task
from ..form.exercise import TaskForm
from ..form.login import HiddenForm


def bold(formulae):
    state = False
    res = ""
    for i in formulae.split('$'):
        if state:
            res += "<b>{}</b>".format(i)
        else:
            res += i
        state = not state
    return res

@source.route('/description/<eid>', methods=['GET', 'POST'])
@login_required
def description(eid):
    if g.user.in_action():
        return redirect(url_for('exercise'))
    ex = Exercise.query.get_or_404(eid)
    form = HiddenForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if request.form['send_button'] == "back":
                return redirect(url_for('exercise'))
            elif request.form['send_button'] == "start":
                new_try = Try.init_try(g.user, ex)
                new_try.start()
                return redirect(url_for('exercise'))
            else:
                pass
    return render_template("description.html", exercise=ex, form=form)


@source.route('/exercise', methods=['GET', 'POST'])
@login_required
def exercise():
    if g.user.in_action():
        return render_current()
    else:
        return render_list()


def render_list():
    exercises = Exercise.query.all()
    shorts = {record.id: -1 for record in exercises}
    tries = g.user.tries
    for i in tries:
        if i.finished_at is not None and\
           i.result >= 0 and\
           (i.result < shorts[i.eid] or shorts[i.eid] == -1):
            shorts[i.eid] = i.result
    return render_template('texts.html', shorts=shorts)


def render_current():
    form = TaskForm()
    current = g.user.tries[-1]

    if 'cancel' in request.form:
        current.finish(False)
        return redirect(url_for('exercise'))

    if form.validate_on_submit():
        task = Task.query.get(form.task_id.data)
        if g.user.id == 1 or check_answer(form.answer.data, task.formulae,
                        dict(map(lambda x: (x.term, loads(x.content.decode("utf8"))), task.contexts))):
            current.next(form.task_id.data)
        else:
            flash("Неправильно!", "error")
        return redirect(url_for('exercise'))

    values = {}
    for task in Task.query.filter_by(group_id=current.step).all():
        lists = []
        for context in task.contexts:
            content = loads(context.content.decode("utf8"))
            size = len(content) if isinstance(content, list) else reduce(lambda x, y: x + len(y), content.values(), 0)
            lists += [(size, context.term, content)]
        values.update({(bold(task.formulae), task.id): lists})
    return render_template('exercise.html', values=values, form=form)
