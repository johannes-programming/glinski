import typing

from isometric import Vector

from .bitBoards import *
from .cells import *
from .motions import *
from .pieces import *
from .players import *

__all__ = ['consts']


class _staticclass:
    def __new__(cls):
        raise NotImplementedError


class consts(_staticclass):
    pass
    

class motions(_staticclass):
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
consts.motions = motions


class vectors(_staticclass):
    pass
vectors.PAWN_WALKS_BY_PLAYER = dict()
for player, motion in consts.motions.PAWN_WALKS_BY_PLAYER.items():
    vectors.PAWN_WALKS_BY_PLAYER[player], = motion
consts.vectors = vectors

class bitBoards(_staticclass):
    pass
bitBoards.promotions = dict()
for player in Player:
    bitBoards.promotions[player] = BitBoard(0)
    for cell in Cell:
        if cell.promotion(player):
            bitBoards.promotions[player] |= cell.flag
consts.bitBoards = bitBoards

