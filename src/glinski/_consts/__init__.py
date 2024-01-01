import typing

from isometric import Vector

from glinski._dataholders.attackerFinders import *
from glinski._dataholders.attackFinders import *
from glinski._dataholders.motions import *
from glinski._dataholders.pieces import *
from glinski._enums.pieces import *
from glinski._enums.players import *

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
        if piece.kind != PieceKind.PAWN:
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
        scaled={PieceKind.BISHOP, PieceKind.QUEEN},
        unscaled={PieceKind.KING},
    )
    FILE = AttackerFinder(
        motion=consts.motions.FILE,
        scaled={PieceKind.ROOK, PieceKind.QUEEN},
        unscaled={PieceKind.KING},
    )
    HORSE = AttackerFinder(
        motion=consts.motions.HORSE,
        unscaled={PieceKind.KNIGHT},
    )
    PAWN_ATTACKS_BY_PLAYER = dict()
consts.attackerFinders = attackerFinders
for player, motion in consts.motions.PAWN_ATTACKS_BY_PLAYER.items():
    consts.attackerFinders.PAWN_ATTACKS_BY_PLAYER[player] = AttackerFinder(
        motion=motion,
        unscaled={PieceKind.PAWN},
    )




