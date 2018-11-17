from time import time
import re


def log(msg):
    with open("tmp/mylog", "a") as fout:
        fout.write("{}:\t{}\n".format(int(time()), repr(msg)))


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
