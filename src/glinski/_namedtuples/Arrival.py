import typing

from isometric import Vector

from glinski._enums import *

__all__ = ['Arrival']

class Arrival(typing.NamedTuple):
    units:typing.FrozenSet[Vector]
    scaled:typing.FrozenSet[PieceType]
    unscaled:typing.FrozenSet[PieceType]



    def __post_init__(self, *args, **kwargs):
        for outerkey, outervalue in self._asdict().items():
            if type(outervalue) is not frozenset:
                raise TypeError(outervalue)
            for innervalue in outervalue:
                if outerkey == 'units':
                    innertype = Vector
                else:
                    innertype = PieceType
                if type(innervalue) is not innertype:
                    raise TypeError(innervalue)
                



    def _direction(self, origin:Cell, unit:Vector):
        maxfactor = 100 if len(self.scaled) else 1
        for n in range(maxfactor):
            cellvector = origin.value + (unit * n)
            try:
                cell = Cell(cellvector)
            except ValueError:
                return
            pieceTypes = self.scaled
            if n == 1:
                pieceTypes = pieceTypes.union(self.unscaled)
            yield cell, pieceTypes
            
    

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
    def from_unit(cls, 
        unit:Vector, 
        *, 
        rotate:bool, 
        unscaled:typing.FrozenSet[PieceType]=frozenset(), 
        scaled:typing.FrozenSet[PieceType]=frozenset(),
    ):
        if type(unit) is not Vector:
            raise TypeError(unit)
        units = list()
        if rotate:
            rotations = range(6)
        else:
            rotations = range(1)
        hands = [unit, unit.hflip()]
        for hand in hands:
            for rotation in rotations:
                v = hand.rotate(rotation)
                units.append(v)
        units = frozenset(units)
        scaled = frozenset(scaled)
        unscaled = frozenset(unscaled)
        return cls(
            units=units,
            scaled=scaled,
            unscaled=unscaled,
        )
    






