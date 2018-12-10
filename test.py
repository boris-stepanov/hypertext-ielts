#!virtualenv/bin/python3

import os
import unittest

from config import Config, basename
from source import source, db
from source.backend import check_answer, flat, drop


class TestCase(unittest.TestCase):
    contexts = {"SIMPLE_LIST": ['SL1'],
                "SIMPLE_DICT": {'SD1': ['SD11']},
                "NORMAL_LIST": ["NL1", "NL2"],
                "NORMAL_DICT": {"ND1": ["ND11", "ND12"],
                                "ND2": ["ND21", "ND22"]},
                "INTERFERENCE_DICT": {"ID1": ["ND11", "ND1", "ID1"],
                                      "ID2": ["ID1"]}}


    def setup(self):
        source.Config['TESTING'] = True
        source.Config['CSRF_ENABLED'] = False
        source.Config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basename, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tear_down(self):
        db.session.remove()
        db.drop_all()

    def test_check_answer(self):
        assert check_answer("", "", self.contexts)
        assert 0 == check_answer("TEST", "", self.contexts)
        assert 0 == check_answer("", "TEST", self.contexts)
        assert 0 == check_answer("", "$NORMAL_LIST$", self.contexts)
        assert 6 == check_answer("abcde ", "abcde $NORMAL_LIST$", self.contexts)
        assert 5 == check_answer("a NL1ID1 a ", "a $NORMAL_LIST$$NORMAL_DICT$ a", self.contexts)
        assert 11 == check_answer("a NL1ND12 a ", "a $NORMAL_LIST$$NORMAL_DICT$ a", self.contexts)
        assert check_answer("NL2", "$NORMAL_LIST$", self.contexts)
        assert check_answer("NL1", "$NORMAL_LIST$", self.contexts)
        assert check_answer("TEST", "TEST", self.contexts)
        assert check_answer("ND11ND11", "$NORMAL_DICT$$INTERFERENCE_DICT$", self.contexts)
        assert check_answer("1 SL1 2 ND21 3", "1 $SIMPLE_LIST$ 2 $NORMAL_DICT$ 3", self.contexts)

    def test_specials(self):
        assert check_answer("A(B)C", "A(B)C", self.contexts)
        assert check_answer("[", "[", self.contexts)
        assert 0 == check_answer("A", ".", self.contexts)

    def test_real_1(self):
        answer = "The pie chart shows the proportion of th asd"
        formulae = "The $N1$ $V1$ the $N2$ of the $Adj1$ $Type2$ $P1$ $Type1$ $Loc1$ $T1$."
        contexts = {"N1": ["pie chart",
                           "diagram",
                           "chart"],
                    "N2": ["proportion",
                           "distribution",
                           "percentage"],
                    "V1": ["depicts",
                           "illustrates",
                           "shows",
                           "compares"],
                    "P1": ["by",
                           "according to"],
                    "Adj1": ["main",
                             "dominant",
                             "most popular"],
                    "Type1": ["fuel type"],
                    "Type2": ["sources of energy",
                              "energy sources"],
                    "T1": ["over the period from 1980 to 1990",
                           "from 1980 to 1990",
                           "in 1980 and 1990",
                           "during the period from 1980 to 1990",
                           "over the decade"],
                    "Loc1": ["in the United States",
                             "in the USA"]}
        assert 40 == check_answer(answer, formulae, contexts)

    def test_drop(self):
        assert drop("of th asdfasdf", "of the ") == 5

    def test_flat(self):
        assert flat(self.contexts) == {"SIMPLE_LIST": {"SL1"},
                                       "SIMPLE_DICT": {"SD11"},
                                       "NORMAL_LIST": {"NL1", "NL2"},
                                       "NORMAL_DICT": {"ND11", "ND12", "ND21", "ND22"},
                                       "INTERFERENCE_DICT": {"ND11", "ND1", "ID1"}}

if __name__ == "__main__":
    unittest.main()
