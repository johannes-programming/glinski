from glinski import _enums
from glinski._namedtuples.Arrival import Arrival as _Arrival

from . import vectors as _vectors

HORSEJUMP = _Arrival.from_unit(
    unit=_vectors.HORSEJUMP,
    rotate=True,
    unscaled=[_enums.PieceType.KNIGHT],
)

FILE = _Arrival.from_unit(
    unit=_vectors.FILE,
    rotate=True,
    scaled=[_enums.PieceType.ROOK, _enums.PieceType.QUEEN],
    unscaled=[_enums.PieceType.KING],
)

DIAGONAL = _Arrival.from_unit(
    unit=_vectors.DIAGONAL,
    rotate=True,
    scaled=[_enums.PieceType.BISHOP, _enums.PieceType.QUEEN],
    unscaled=[_enums.PieceType.KING],
)

BLACK_PAWN_ATTACK = _Arrival.from_unit(
    unit=_vectors.BLACK_PAWN_ATTACK,
    rotate=False,
    unscaled=[_enums.PieceType.PAWN],
)

WHITE_PAWN_ATTACK = _Arrival.from_unit(
    unit=_vectors.WHITE_PAWN_ATTACK,
    rotate=False,
    unscaled=[_enums.PieceType.PAWN],
)

