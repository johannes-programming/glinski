# imports
import typing

from isometric import Vector
from staticclasses import staticclass

from .bitBoards import *
from .cells_and_files import *
from .motions import *
from .pieces import *
from .players import *

# __all__
__all__ = ['consts']




# classes
class consts(staticclass):
    @classmethod
    def _setup(cls):
        # vectors
        for p, m in consts.motions.PAWN_WALKS_BY_PLAYER.items():
            cls.vectors.PAWN_WALKS_BY_PLAYER[p], = m
        # bitBoards
        black_promotions = BitBoard.by_cells(f[1] for f in File)
        cls.bitBoards.promotions = {
            Player.BLACK: black_promotions,
            Player.WHITE: black_promotions.turntable(),
        }
        white_ep_cells = {
            Cell.b6, Cell.c6, Cell.d6,
            Cell.e6, Cell.f6, Cell.g6,
            Cell.h6, Cell.i6, Cell.k6,
        }
        white_eps = BitBoard.by_cells(white_ep_cells)
        cls.bitBoards.eps = {
            Player.WHITE: white_eps,
            Player.BLACK: white_eps.turntable(),
        }
    class motions(staticclass):
        HORSE = Motion(Vector(y=-1, z=2), rotate=True)
        LINE = Motion(Vector(z=1), rotate=True)
        DIAGONAL = Motion(Vector(y=-1, z=1), rotate=True)
        PAWN_ATTACKS_BY_PLAYER = {
            Player.WHITE:Motion(Vector(y=-1), rotate=False),
            Player.BLACK:Motion(Vector(y=1), rotate=False),
        }
        PAWN_WALKS_BY_PLAYER = {
            Player.WHITE:Motion(Vector(z=1), rotate=False),
            Player.BLACK:Motion(Vector(z=-1), rotate=False),
        }
    class vectors(staticclass):
        PAWN_WALKS_BY_PLAYER = dict()
    class bitBoards(staticclass):
        pass
consts._setup()


