import isometric as _iso

FILE = _iso.Vector(z=1)
DIAGONAL = _iso.Vector(y=-1, z=1)
HORSEJUMP = _iso.Vector(y=-1, z=2)
BLACK_PAWN_ATTACK = _iso.Vector(y=1)
WHITE_PAWN_ATTACK = BLACK_PAWN_ATTACK.vflip()
BLACK_PAWN_WALK = _iso.Vector(z=-1)
WHITE_PAWN_WALK = BLACK_PAWN_ATTACK.vflip()