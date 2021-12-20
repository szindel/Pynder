from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class ResultMatch:
    """Class for keeping track of an item in inventory.

    This class serves as a interface to have homogenous output for every analyzed question on a text.
    We define add and radd functions for easy later use, mind you the order of the lists are crucial.
    all index 0 of the iterables are the same match. Orders of lists/tuples are guaranteed hence safe.

    Example usage:

    a1 = ResultMatch(True, ['test', 'test2', 'test3'], [1,5,9], ['doc1', 'doc1', 'doc1'])
    a2 = ResultMatch(True, ['test11', 'test2', 'test91'], [1,5, 10], ['doc2', 'doc2', 'doc2'])
    a3 = ResultMatch(False)

    -> sum([a1,a2, a3])
    -> a1+a2
    """

    bResult: bool = False
    tMatches: tuple = ()
    tPage_nr: tuple = ()
    tDocIds: tuple = ()  # should be redundant but its easier for later merging in excel

    def __post_init__(self):
        assert isinstance(self.bResult, bool), f"type found: {type(self.bResult)}"
        assert isinstance(self.tMatches, tuple), f"type found: {type(self.tMatches)}"
        assert isinstance(self.tPage_nr, tuple), f"type found: {type(self.tPage_nr)}"
        assert isinstance(self.tDocIds, tuple), f"type found: {type(self.tDocIds)}"

        # if no match than these attributes cant be filled
        if not self.bResult:
            assert not bool(
                self.tMatches
            ), "iMatches can't be filled if bResult is False"
            assert not bool(
                self.tPage_nr
            ), "iPage_nr can't be filled if bResult is False"
            assert not bool(self.tDocIds), "iDocIds can't be filled if bResult is False"

        # if these are filled, they need to be filled with the same amount of entries (index is crucial)
        assert len(self.tMatches) == len(
            self.tPage_nr
        ), "number of matches need to equal number of pages"
        assert len(self.tMatches) == len(
            self.tDocIds
        ), "Number of matches need to equal the number of doc IDs"

    def __add__(self, other):
        return ResultMatch(
            bResult=bool(self.bResult + other.bResult),
            # below is all tuple addition hence safe
            tMatches=self.tMatches + other.tMatches,
            tPage_nr=self.tPage_nr + other.tPage_nr,
            tDocIds=self.tDocIds + other.tDocIds,
        )

    def __radd__(self, other):
        if other == 0:  # needed for init sum
            return self
        else:
            return self.__add__(other)
