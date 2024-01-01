import typing
from dataclasses import dataclass

from isometric import Vector

from glinski._enums import *

from .motions import *

__all__ = ['AttackFinder']

@dataclass(frozen=True)
class BaseAttackFinder:
    # fields
    maxfactor: int
    motions: typing.FrozenSet[Motion]

    # methods
    #   private
    def _direction(self, 
        origin:Cell, *,
        unit:Vector,
    ) -> typing.Generator[Cell, None, None]:
        generator = origin.count_up(
            start=1,
            stop=self.maxfactor+1,
            vector=unit,
        )
        for n, cell in generator:
            yield cell
    
    #   public
    def directions(self, 
        origin:Cell,
    ) -> typing.Generator[
        typing.Generator[Cell, None, None],
        None,
        None,
    ]:
        if type(origin) is not Cell:
            raise TypeError(origin)
        for m in self.motions:
            for u in m:
                yield self._direction(origin, unit=u)
    
    @property
    def radii(self):
        return frozenset(abs(m) for m in self.motions)

    


class AttackFinder(BaseAttackFinder):
    def __init__(self, 
        *motions,
        maxfactor:int = 100,
    ):
        if type(maxfactor) is not int:
            raise TypeError(maxfactor)
        motions = frozenset(motions)
        for motion in motions:
            if type(motion) is not Motion:
                raise TypeError(motion)
        super().__init__(
            maxfactor=maxfactor, 
            motions=motions,
        )
