import enum as _enum

__all__ = ['PlayerColor']

class PlayerColor(_enum.Enum):
    BLACK = False
    WHITE = True
    def invert(self):
        cls = type(self)
        value = not self.value
        ans = cls(value)
        return ans