"""
Pure backend code
"""
from typing import Dict, List, Union
from datetime import datetime
from os.path import join
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


def check_answer(answer: str, formulae: str, contexts) -> Union[bool, int]:
    flatten = flat(contexts)
    parts = formulae.split('$')
    cdr = drop(answer, parts[0])
    if isinstance(cdr, int):
        return cdr
    res = recursive_check(cdr, parts[1:], flatten)
    if res is True:
        return True
    return res + len(parts[0])


def drop(answer: str, part: str):
    for pos, char in enumerate(part):
        if not answer or answer[0] != char:
            return pos
        answer = answer[1:]
    return answer


def recursive_check(answer: str, parts: List[str], contexts: Dict[str, str]):
    if not answer and not parts:
        return True
    if not answer or not parts:
        return 0
    res = 0
    for context in contexts[parts[0]]:
        cdr = drop(answer, context)
        if isinstance(cdr, int):
            continue
        cdr = drop(cdr, parts[1])
        if isinstance(cdr, int):
            res = max(res, len(context) + cdr)
            continue
        i = recursive_check(cdr, parts[2:], contexts)
        if i is True:
            return True
        res = max(res, len(context) + i + len(parts[1]))
    return res


def flat(contexts):
    flatten: Dict[int, str] = {}
    for i, verb in contexts.items():
        if isinstance(verb, list):
            flatten[i] = set(verb)
        else:
            flatten[i] = set().union(*map(set, verb.values()))
    return flatten
