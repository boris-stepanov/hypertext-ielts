"""
Pure backend code
"""
from typing import Dict, List, Union
from datetime import datetime
from os.path import join
import re
from config import basename


def log(msg):
    with open(join(basename, "tmp/mylog"), "a") as fout:
        fout.write("{}:\t{}\n".format(datetime.now(), repr(msg)))


def list_user_tries(default: Dict[int, List[Union[int, bool]]], tries) -> None:
    for i in tries:
        eid = i.eid
        if i.finished_at is not None and i.result >= 0:
            default[eid][0] += 1
        elif i.finished_at is None:
            default[eid][1] = True


def check_answer(answer: str, formulae: str, contexts) -> bool:
    state = True
    flatten = flat(contexts)
    parts = []
    for i in formulae.split('$'):
        if state:
            parts.append(replace_special(i))
        else:
            parts.append("({})".format("|".join(flatten[i])))
        state = not state
    pat = "".join(parts)
    return bool(re.fullmatch(pat, answer.strip(), re.IGNORECASE))


def replace_special(formulae: str) -> str:
    special = {'(', ')', '[', ']', '.', '*', '^', '?', '+', '{', '}', '|'}
    for i in special:
        formulae = formulae.replace(i, "\\"+i)
    return formulae


def flat(contexts):
    flatten: Dict[int, str] = {}
    for i, verb in contexts.items():
        if isinstance(verb, list):
            flatten[i] = set(verb)
        else:
            flatten[i] = set().union(*map(set, verb.values()))
    return flatten
