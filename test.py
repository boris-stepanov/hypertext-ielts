#!virtualenv/bin/python3

import os
import unittest

from config import Config, basename
from source import source, db
from source.backend import check_answer, flat


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
        assert not check_answer("TEST", "", self.contexts)
        assert not check_answer("", "TEST", self.contexts)
        assert not check_answer("", "$NORMAL_LIST$", self.contexts)
        assert check_answer("NL2", "$NORMAL_LIST$", self.contexts)
        assert check_answer("NL1", "$NORMAL_LIST$", self.contexts)
        assert check_answer("TEST", "TEST", self.contexts)
        assert check_answer("ND11ND11", "$NORMAL_DICT$$INTERFERENCE_DICT$", self.contexts)
        assert check_answer("1 SL1 2 ND21 3", "1 $SIMPLE_LIST$ 2 $NORMAL_DICT$ 3", self.contexts)

    def test_flat(self):
        assert flat(self.contexts) == {"SIMPLE_LIST": {"SL1"},
                                       "SIMPLE_DICT": {"SD11"},
                                       "NORMAL_LIST": {"NL1", "NL2"},
                                       "NORMAL_DICT": {"ND11", "ND12", "ND21", "ND22"},
                                       "INTERFERENCE_DICT": {"ND11", "ND1", "ID1"}}

if __name__ == "__main__":
    unittest.main()
