"""
All exercise related routes
"""
from typing import Dict, List, Tuple
from functools import reduce
from json import loads
from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from source import source, check_answer, list_user_tries, db, log
from ..model import Exercise, Try, Task
from ..form.exercise import TaskForm
from ..form.login import HiddenForm


def bold(formulae: str) -> str:
    """
    Replace '$' in formulas with bold tag
    """
    state = False
    res = ""
    for i in formulae.split('$'):
        if state:
            res += "<b>{}</b>".format(i)
        else:
            res += i
        state = not state
    return res


@source.route('/texts', methods=['GET', 'POST'])
def texts():
    exercises = Exercise.query.all()
    shorts = {record.id: [0, False] for record in exercises}
    # shorts: Dict[int, Tuple[bool, bool]]
    list_user_tries(shorts, current_user.get_tries())
    return render_template('texts.html', shorts=shorts)


@source.route('/description/<eid>', methods=['GET', 'POST'])
def description(eid: str) -> str:
    if current_user.get_try(int(eid)):
        return redirect(url_for('exercise', eid=eid))

    ex = Exercise.query.get_or_404(eid)
    form = HiddenForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if request.form['send_button'] == "back":
                return redirect(url_for('texts'))

            if request.form['send_button'] == "start":
                new_try = Try.init(current_user, ex)
                db.session.refresh(new_try)
                return redirect(url_for('exercise', eid=eid))

    return render_template("description.html", exercise=ex, form=form)


@source.route('/exercise/<eid>', methods=['GET', 'POST'])
def exercise(eid: str) -> str:
    current = current_user.get_try(int(eid))
    if not current:
        return redirect(url_for('description', eid=eid))
    form = TaskForm()

    if 'cancel' in request.form:
        current.finish(False)
        return redirect(url_for('texts'))

    log(current)
    if form.validate_on_submit():
        task = Task.query.get(form.task_id.data)
        if True or current_user.get_id() == 1 or \
           check_answer(form.answer.data,
                        task.formulae,
                        dict(map(lambda x: (x.term,
                                            loads(x.content.decode("utf8"))),
                                 task.contexts))):
            current.append(form.answer.data)
            if current.next():
                return redirect(url_for('texts'))
        else:
            flash("Неправильно!", "error")
        return redirect(url_for('exercise', eid=eid))

    values: Dict[Tuple[str, int], List[Tuple[int, str, str]]] = {}
    for task in Task.query.filter_by(group_id=current.step).all():
        lists: List[Tuple[int, str, str]] = []
        for context in task.contexts:
            content = loads(context.content.decode("utf8"))
            if isinstance(content, list):
                size = len(content)
            else:
                size = reduce(lambda x, y: x + len(y), content.values(), 0)
            lists += [(size, context.term, content)]
        values.update({(bold(task.formulae), task.id): lists})
    return render_template('exercise.html',
                           eid=eid,
                           values=values,
                           form=form,
                           text=current.text)
