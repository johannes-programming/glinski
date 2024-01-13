import typing
from dataclasses import dataclass

from isometric import Vector

__all__ = ['Motion']


@dataclass(frozen=True)
class BaseMotion:
    # fields
    _abs: float
    _items: typing.FrozenSet[Vector]


class Motion(BaseMotion):
    # methods
    #   dunder
    def __abs__(self):
        return self._abs
    def __init__(self, unit:Vector, *, rotate:bool) -> None:
        if type(unit) is not Vector:
            raise TypeError(unit)
        if type(rotate) is not bool:
            raise TypeError(rotate)
        hands = [unit, unit.hflip()]
        if rotate:
            rotations = range(6)
        else:
            rotations = range(1)
        items = set()
        for hand in hands:
            for rotation in rotations:
                items.add(hand.rotate(rotation))
        super().__init__(
            _abs=float(abs(unit)),
            _items=frozenset(items),
        )
    def __iter__(self):
        return iter(self._items)
    def __len__(self):
        return len(self._items)
