from enum import Enum

from .players import *

__all__ = ['Termination']

class Termination(Enum):
    CHECKMATE = 1
    STALEMATE = 2
    INSUFFICIENT_MATERIAL = 3
    SEVENTYFIVE_MOVES = 4
    FIVEFOLD_REPETITION = 5
    FIFTY_MOVES = 6
    THREEFOLD_REPETITION = 7
    def result(self) -> float:
        cls = type(self)
        ans = {
            cls.CHECKMATE:1.00,
            cls.STALEMATE:0.75,
        }.get(self, 0.50)
        return ans
    
