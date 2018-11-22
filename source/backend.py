from datetime import datetime
from os.path import join
import re
from config import basename


def log(msg):
    with open(join(basename, "tmp/mylog"), "a") as fout:
        fout.write("{}:\t{}\n".format(datetime.now(), repr(msg)))


def check_answer(answer, formulae, contexts):
    state = True
    contexts = flat(contexts)
    pat = []
    for i in formulae.split('$'):
        if state:
            pat.append(i)
        else:
            pat.append("(" + "|".join(contexts[i]) + ")")
        state = not state
    pat = "".join(pat)
    return bool(re.fullmatch(pat, answer.strip(), re.IGNORECASE))

def flat(contexts):
    flatten = {}
    for i, v in contexts.items():
        if isinstance(v, list):
            flatten[i] = set(v)
        else:
            flatten[i] = set().union(*map(set, v.values()))
    return flatten
