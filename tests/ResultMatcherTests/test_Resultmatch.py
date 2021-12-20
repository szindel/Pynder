from pynder.enums import ResultMatch

import unittest
import pytest


class TestsPipelineInit(unittest.TestCase):
    def test_Resultmatch1(self):
        assert ResultMatch()

    def test_Resultmatch2(self):
        assert ResultMatch(
            True, tMatches=("test", "test2"), tPage_nr=(1, 2), tDocIds=(101, 102)
        )

    def test_Resultmatch3(self):
        total_result = ResultMatch() + ResultMatch(
            True, tMatches=("test", "test2"), tPage_nr=(1, 2), tDocIds=(101, 102)
        )
        assert total_result == ResultMatch(
            True, tMatches=("test", "test2"), tPage_nr=(1, 2), tDocIds=(101, 102)
        )

    def test_Resultmatch4(self):
        res1 = ResultMatch(
            True, tMatches=("test1", "test2"), tPage_nr=(1, 2), tDocIds=(101, 102)
        )
        res2 = ResultMatch(
            True, tMatches=("test3", "test4"), tPage_nr=(3, 4), tDocIds=(104, 105)
        )

        assert res1 + res2 == ResultMatch(
            True,
            tMatches=("test1", "test2", "test3", "test4"),
            tPage_nr=(1, 2, 3, 4),
            tDocIds=(101, 102, 104, 105),
        )
