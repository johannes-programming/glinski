import typing

from isometric import Vector

from .attackerFinders import *
from .attackFinders import *
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
    FILE = Motion(Vector(z=1), rotate=True)
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


class attackFinders(_staticclass):
    @classmethod
    def finder(cls, piece:Piece):
        if type(piece) is not Piece:
            raise TypeError(piece)
        if piece.kind != Piece.Kind.PAWN:
            return getattr(cls, piece.kind.name)
        return getattr(cls, piece.player.name + '_PAWN_ATTACK')
    WHITE_PAWN_ATTACK = AttackFinder(
        consts.motions.PAWN_ATTACKS_BY_PLAYER[Player.WHITE],
        maxfactor=1,
    )
    BLACK_PAWN_ATTACK = AttackFinder(
        consts.motions.PAWN_ATTACKS_BY_PLAYER[Player.BLACK],
        maxfactor=1,
    )
    KNIGHT = AttackFinder(
        consts.motions.HORSE,
        maxfactor=1,
    )
    BISHOP = AttackFinder(
        consts.motions.DIAGONAL,
    )
    ROOK = AttackFinder(
        consts.motions.FILE,
    )
    QUEEN = AttackFinder(
        consts.motions.DIAGONAL,
        consts.motions.FILE,
    )
    KING = AttackFinder(
        consts.motions.DIAGONAL,
        consts.motions.FILE,
        maxfactor=1,
    )
consts.attackFinders = attackFinders


class attackerFinders:
    @classmethod
    def finders(cls, 
        player:Player,
    ) -> typing.Generator[AttackerFinder, None, None]:
        yield cls.DIAGONAL
        yield cls.FILE
        yield cls.HORSE
        yield cls.PAWN_ATTACKS_BY_PLAYER[player]

    DIAGONAL = AttackerFinder(
        motion=consts.motions.DIAGONAL,
        scaled={Piece.Kind.BISHOP, Piece.Kind.QUEEN},
        unscaled={Piece.Kind.KING},
    )
    FILE = AttackerFinder(
        motion=consts.motions.FILE,
        scaled={Piece.Kind.ROOK, Piece.Kind.QUEEN},
        unscaled={Piece.Kind.KING},
    )
    HORSE = AttackerFinder(
        motion=consts.motions.HORSE,
        unscaled={Piece.Kind.KNIGHT},
    )
    PAWN_ATTACKS_BY_PLAYER = dict()
consts.attackerFinders = attackerFinders
for player, motion in consts.motions.PAWN_ATTACKS_BY_PLAYER.items():
    consts.attackerFinders.PAWN_ATTACKS_BY_PLAYER[player] = AttackerFinder(
        motion=motion,
        unscaled={Piece.Kind.PAWN},
    )



