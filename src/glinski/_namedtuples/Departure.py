import typing

from isometric import Vector

from glinski._enums import *

__all__ = ['Departure']

class Departure(typing.NamedTuple):
    units:typing.FrozenSet[Vector]
    maxfactor:int = 100

    def __post_init__(self, *args, **kwargs):
        if type(self.maxfactor) is not int:
            raise TypeError(self.maxfactor)
        if self.maxfactor < 1:
            raise ValueError(self.maxfactor)
        if type(self.units) is not frozenset:
            raise TypeError(self.units)
        for unit in self.units:
            if type(unit) is not Vector:
                raise TypeError(unit)

    def _direction(self, origin:Cell, unit:Vector):
        for n in range(1, self.maxfactor + 1):
            cellvector = origin.value + (unit * n)
            try:
                cell = Cell(cellvector)
            except ValueError:
                return
            yield cell

    def directions(self, origin:typing.Union[str, Cell, Vector]):
        if type(origin) is Vector:
            origin = Cell(origin)
        if type(origin) is str:
            origin = Cell[origin]
        if type(origin) is not Cell:
            raise TypeError(origin)
        for unit in self.units:
            yield self._direction(origin=origin, unit=unit)

    @classmethod
    def from_units(cls, 
        *units,  
        rotate:bool, 
        maxfactor:int,
    ):
        if rotate:
            rotations = range(6)
        else:
            rotations = range(1)
        moreunits = list()
        for unit in units:
            if type(unit) is not Vector:
                raise TypeError(unit)
            for hand in [unit, unit.hflip()]:
                for rotation in rotations:
                    v = hand.rotate(rotation)
                    moreunits.append(v)
        moreunits = frozenset(moreunits)
        return cls(
            units=moreunits,
            maxfactor=maxfactor,
        )
    
    def radii(self):
        return [float(abs(u)) for u in self.units]



