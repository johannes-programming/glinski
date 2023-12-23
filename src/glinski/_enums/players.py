from enum import Enum

__all__ = ['Player']

class Player(Enum):
    BLACK = False
    WHITE = True
    def invert(self):
        cls = type(self)
        value = not self.value
        ans = cls(value)
        return ans
