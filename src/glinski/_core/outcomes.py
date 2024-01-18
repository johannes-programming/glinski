# imports
from enum import Enum

from .players import *

# __all__
__all__ = ['Outcome']




# class
class Outcome(Enum):
    FULL_WIN_FOR_BLACK = (0.00, 1.00)
    HALF_WIN_FOR_BLACK = (0.25, 0.75)
    DRAW = (0.50, 0.50)
    HALF_WIN_FOR_WHITE = (0.75, 0.25)
    FULL_WIN_FOR_WHITE = (1.00, 0.00)
    @classmethod
    def by_items(cls, white=None, black=None):
        if white is not None:
            white = float(white)
        if black is not None:
            black = float(black)
        if white is None:
            if black is None:
                return None
            else:
                return cls((1 - black, black))
        else:
            if black is None:
                return cls((white, 1 - white))
            else:
                return cls((white, black))
    def for_player(self, player:Player) -> float:
        player = Player(player)
        if player == Player.BLACK:
            return self.value[1]
        else:
            return self.value[0]
    def swapplayer(self):
        cls = type(self)
        value = self.value[::-1]
        ans = cls(value)
        return ans
    def to_dict(self):
        return {
            p:self.for_player(p)
            for p in Player
        }
    


