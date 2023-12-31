import typing
from dataclasses import dataclass

from isometric import Vector

from glinski._enums import *

from .motions import *

__all__ = ['AttackerFinder']

@dataclass(frozen=True)
class BaseAttackerFinder:
    motion:Motion
    scaled:typing.FrozenSet[PieceKind]
    unscaled:typing.FrozenSet[PieceKind]

    def _direction(self, *,
        origin:Cell, 
        unit:Vector,
    ) -> typing.Generator[
        typing.Tuple[Cell, typing.FrozenSet[PieceKind]], 
        None, 
        None,
    ]:
        maxfactor = 100 if len(self.scaled) else 1
        generator = origin.count_up(
            start=1,
            stop=maxfactor+1,
            vector=unit,
        )
        for n, cell in generator:
            if n == 1:
                yield cell, self.scaled.union(self.unscaled)
            else:
                yield cell, self.scaled
    def directions(self, origin:Cell):
        if type(origin) is not Cell:
            raise TypeError(origin)
        for unit in self.motion:
            yield self._direction(origin=origin, unit=unit)


class AttackerFinder(BaseAttackerFinder):
    def __init__(self, 
        *,
        motion:Motion,
        scaled:typing.Iterable[PieceKind]=[],
        unscaled:typing.Iterable[PieceKind]=[],
    ) -> None:
        if type(motion) is not Motion:
            raise TypeError(motion)
        scaled = frozenset(scaled)
        unscaled = frozenset(unscaled)
        for f in (scaled, unscaled):
            for t in f:
                if type(t) is not PieceKind:
                    raise TypeError(t)
        super().__init__(
            motion=motion,
            scaled=scaled,
            unscaled=unscaled,
        )
    






