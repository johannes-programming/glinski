from enum import Enum
import typing

from .players import *

__all__ = ['TerminationKind']

class TerminationKind(Enum):
    CHECKMATE = 1
    STALEMATE = 2
    AGREEMENT = 3
    SEVENTYFIVE_MOVES = 4
    FIVEFOLD_REPETITION = 5
    FIFTY_MOVES = 6
    THREEFOLD_REPETITION = 7
    RESIGNATION = 8
    
    def for_subject(self) -> typing.:
        cls = type(self)
        ans = {
            cls.CHECKMATE:1.00,
            cls.STALEMATE:0.75,
            cls.AGREEMENT:None,
            cls.SEVENTYFIVE_MOVES:0.50,
            cls.FIVEFOLD_REPETITION:0.50,
            cls.FIFTY_MOVES:0.50,
            cls.THREEFOLD_REPETITION:0.50,
            cls.RESIGNATION:0.00
        }[self]
        return ans
    def for_opponent(self):
        x = self.for_subject()
        if x is None:
            return None
        return 1.0 - x


    
