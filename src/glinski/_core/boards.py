# imports
from string import digits
from typing import Any, Iterable, Optional, Self, overload

from isometric import Vector

from .bitBoards import *
from .cells_and_files import *
from .cli import *
from .consts import *
from .errors import *
from .pieces import *
from .players import *
from .strangeFuncs import *

# __all__
__all__ = ['Board']




# classes
class Board:

    # magic methods
    def __bool__(self) -> bool:
        return any(self._bitBoards)
    def __eq__(self, other) -> bool:
        cls = type(self)
        if type(other) is not cls:
            return False
        return self._bitBoards == other._bitBoards
    @overload 
    def __init__(self) -> None:
        ...
    def _init_clone(self, o:Self, /) -> None:
        self._bitBoards = o._bitBoards
        self._fen = o._fen
    @overload
    def __init__(self, fen:Any) -> None:
        ...
    def _init_fen(self, fen:Any) -> None:
        self._bitBoards = self._parse_fen(fen)
        self._fen = self._calc_fen()
    @overload
    def __init__(self, 
        P:BitBoard=0, N:BitBoard=0, B:BitBoard=0, 
        R:BitBoard=0, Q:BitBoard=0, K:BitBoard=0, 
        p:BitBoard=0, n:BitBoard=0, b:BitBoard=0, 
        r:BitBoard=0, q:BitBoard=0, k:BitBoard=0,
    ) -> None:
        ...
    def _init_bitBoards(self, 
        P:BitBoard=0, N:BitBoard=0, B:BitBoard=0, 
        R:BitBoard=0, Q:BitBoard=0, K:BitBoard=0, 
        p:BitBoard=0, n:BitBoard=0, b:BitBoard=0, 
        r:BitBoard=0, q:BitBoard=0, k:BitBoard=0,
    ) -> None:
        self._bitBoards = self._format_bitBoards(
            P, N, B, R, Q, K, p, n, b, r, q, k,
        )
        self._fen = self._calc_fen()
    def __init__(self, *args, **kwargs) -> None:
        cls = type(self)
        if (len(args) == 1) and (len(kwargs) == 0):
            if type(args[0]) is cls:
                self._init_clone(args[0])
                return
            if not issubclass(type(args[0]), int):
                self._init_fen(**kwargs)
                return
        if (len(args) == 0) and (len(kwargs) == 1):
            if set(kwargs.keys()) == {'fen'}:
                self._init_fen(**kwargs)
                return
        self._init_bitBoards(*args, **kwargs)
    def __repr__(self) -> str:
        return self.text()
    def __str__(self) -> str:
        return self.fen


    # calc
    def _calc_fen(self) -> str:
        cls = type(self)
        ans = ""
        for cells in cls._RANKS:
            empty = 0
            for cell in cells:
                piece = self.piece(cell)
                if piece is None:
                    empty += 1
                    continue
                if empty:
                    ans += str(empty)
                    empty = 0
                ans += piece.fen
            if empty:
                ans += str(empty)
            ans += '/'
        ans = ans[:-1]
        return ans
    

    # other protected methods
    @classmethod
    def _axial_attacks(cls, 
        origin:Cell, *, 
        allowed:BitBoard,
        occupied:BitBoard,
    ):
        ans = BitBoard(0)
        for i in range(6):
            j = occupied.axial_gap(origin, direction=i)
            ans |= BitBoard.axial_mask(origin, direction=i, gap=j)
            if j != -1:
                ans |= origin.axial_ray(i)[j].flag & allowed
        return ans
    @classmethod
    def _diagonal_attacks(cls, 
        origin:Cell, *, 
        allowed:BitBoard,
        occupied:BitBoard,
    ):
        ans = BitBoard(0)
        for i in range(6):
            j = occupied.diagonal_gap(origin, direction=i)
            ans |= BitBoard.diagonal_mask(origin, direction=i, gap=j)
            if j != -1:
                ans |= origin.diagonal_ray(i)[j].flag & allowed
        return ans
    @classmethod
    def _envs(vectors:Iterable[Vector]):
        ans = [BitBoard(0)] * 91
        for cell in Cell:
            search = cell.search(vectors)
            for s in search:
                ans[cell] |= s.flag
        ans = tuple(ans)
        return ans
    @classmethod
    def _find_fen_piece(cls, string):
        for i, s in enumerate(string):
            if s not in digits:# do not change!
                return i
        return len(string)
    @classmethod
    def _format_bitBoards(cls, *bitBoards):
        taken = BitBoard(0)
        for i in range(12):
            bitBoards[i] = BitBoard(bitBoards[i])
            if taken & bitBoards[i]:
                raise ValueError
            taken |= bitBoards[i]
        return bitBoards
    @classmethod
    def _parse_fen(cls, fen:str):
        fen = str(fen)
        boardpieces = [""] * 91
        parts = fen.split('/')
        if len(parts) != 11:
            raise ValueError(fen)
        for part, cells in zip(parts, cls._RANKS):
            rankpieces = cls._parse_fen_rank(part)
            if len(rankpieces) != len(cells):
                raise ValueError(fen)
            for piece, cell in zip(rankpieces, cells):
                boardpieces[cell] = piece
        ans = [0] * 12
        for cell in Cell:
            piece = boardpieces[cell]
            if piece is None:
                continue
            ans[piece] |= cell.flag
        ans = tuple(BitBoard(x) for x in ans)
        return ans
    @classmethod
    def _parse_fen_rank(cls, string):
        ans = list()
        while string:
            i = cls._find_fen_piece(string)
            if i:
                j = int(string[:i])
                ans += [None] * j
                string = string[i:]
                continue
            ans.append(Piece.by_fen(string[0]))
            string = string[1:]
        return ans
    @classmethod
    def _setup(cls):
        # fen ranks
        cls._RANKS = list()
        for rank in range(11, 0, -1):
            ranklist = list()
            for f in range(11):
                file = File(f)
                if len(file) < rank:
                    continue
                cell = file[rank]
                ranklist.append(cell)
            cls._RANKS.append(ranklist)
        # pawn bans
        ranks = [1, 8, 9, 10, 11]
        cells = {c for c in Cell if (c.rank in ranks)}
        bb = BitBoard.by_cells(cells)
        cls._PAWN_BAN_BY_PLAYER = dict()
        cls._PAWN_BAN_BY_PLAYER[Player.BLACK] = bb
        cls._PAWN_BAN_BY_PLAYER[Player.WHITE] = bb.turntable()
        # non sliding environments
        cls._KNIGHT_ENV = cls._envs(consts.motions.HORSE)
        cls._KING_ENV = cls._envs(
            list(consts.motions.LINE)
            + list(consts.motions.DIAGONAL)
        )
        cls._PAWN_ENV_BY_PLAYER = dict()
        for player in Player:
            cls._PAWN_ENV_BY_PLAYER[player] = cls._envs(
                consts.motions.PAWN_ATTACKS_BY_PLAYER[player]
            )
        # native
        change = {c:c.native() for c in Cell}
        cls._NATIVE = cls().apply(change)


    # properties
    @property
    def fen(self) -> str:
        return self._fen


    # boolean methods
    def is_check(self, turn:Player) -> bool:
        return bool(self.checkers(turn.turntable()))
    def is_illegal_king(self) -> bool:
        for king in [Piece.k, Piece.K]:
            bitBoard = self.bitBoard(king)
            if all((c.flag != bitBoard) for c in Cell):
                return True
        return False
    def is_illegal_pawn(self) -> bool:
        cls = type(self)
        for player in Player:
            pawn = player * 6
            if self.bitBoard(pawn) & cls._PAWN_BAN_BY_PLAYER[player]:
                return True
        return False


    # other public methods
    def apply(self, change) -> Self:
        cls = type(self)
        change = dict(change)
        change = {Cell(k):v for k, v in change.items()}
        changemask = BitBoard.by_cells(change.keys())
        keepmask = ~changemask
        bitBoards = list()
        for piece in range(12):
            bitBoard = self.bitBoard(piece)
            bitBoard &= keepmask
            bitBoards.append(bitBoard)
        for cell, piece in change.items():
            if piece is not None:
                bitBoards[piece] |= cell.flag
        ans = cls(*bitBoards)
        return ans
    def attackers(self, 
        cell:Cell, *,
        player:Optional[Player]=None,
    ) -> BitBoard:
        cls = type(self)
        cell = Cell(cell)
        if player is None:
            player = self.piece(cell).player.turntable()
        else:
            player = Player(player)
        #
        ans = BitBoard(0)
        #
        pawn = player * 6 + 0
        knight = player * 6 + 1
        bishop = player * 6 + 2
        rook = player * 6 + 3
        queen = player * 6 + 4
        king = player * 6 + 5
        #
        pawn_envs = cls._PAWN_ENV_BY_PLAYER[player.turntable()]
        ans |= self.bitBoard(pawn) & pawn_envs[cell]
        ans |= self.bitBoard(knight) & cls._KNIGHT_ENV[cell]
        ans |= self.bitBoard(king) & cls._KING_ENV[cell]
        #
        occupied = self.occupied()
        danger = self.bitBoard(bishop) | self.bitBoard(queen)
        for i in range(6):
            j = occupied.diagonal_gap(cell, direction=i)
            if j != -1:
                ans |= cell.diagonal_ray(i)[j].flag & danger
        danger = self.bitBoard(rook) | self.bitBoard(queen)
        for i in range(6):
            j = occupied.axial_gap(cell, direction=i)
            if j != -1:
                ans |= cell.axial_ray(i)[j].flag & danger
        ans = BitBoard(ans)
        return ans
    def attacks(self,
        cell:Cell, *,
        piece:Optional[Piece]=None,
    ) -> BitBoard:
        cls = type(self)
        cell = Cell(cell)
        if piece is None:
            piece = self.piece(cell)
        else:
            piece = Piece(piece)
        if piece is None:
            return BitBoard(0)
        player = piece.player
        kind = int(piece.kind)
        allowed = ~self.occupied(player)
        #
        if kind == 0: # pawn
            envs = cls._PAWN_ENV_BY_PLAYER[player]
            return allowed & envs[cell]
        if kind == 1: # knight
            return allowed & cls._KNIGHT_ENV[cell]
        if kind == 5: # king
            return allowed & cls._KING_ENV[cell]
        #
        occupied = self.occupied()
        ans = BitBoard(0)
        if kind in {2, 4}: # bishop or queen
            ans |= self._diagonal_attacks(
                cell, 
                allowed=allowed, 
                occupied=occupied,
            )
        if kind in {3, 4}: # rook or queen
            ans |= self._axial_attacks(
                cell, 
                allowed=allowed, 
                occupied=occupied,
            )
        return ans
    def bitBoard(self, piece:Piece):
        piece = Piece(piece)
        ans = self._bitBoards[piece]
        return ans
    def checkers(self, player:Player) -> BitBoard: 
        player = Player(player)
        ans = BitBoard(0)
        for c in Cell:
            p = self.piece(c)
            if p is None:
                continue
            if p.player == player:
                continue
            if p.kind != Piece.Kind.KING:
                continue
            ans |= self.attackers(
                c,
                player=player,
            )
        return ans
    @classmethod
    def native(cls) -> Self: 
        return cls._NATIVE
    def occupied(self, 
        player:Optional[Player]=None,
    ) -> BitBoard:
        if player is None:
            a = 0
            b = 12
        else:
            player = Player(player)
            a = 6 * player
            b = 6 * (player + 1)
        ans = BitBoard(0)
        for i in range(a, b):
            ans |= self.bitBoard(i)
        return ans
    def piece(self, 
        cell:Cell,
    ) -> Piece: 
        cell = Cell(cell)
        flag = cell.flag
        for ans in Piece:
            if flag & self.bitBoard(ans):
                return ans
        return None
    def text(self) -> str:
        symbols = ['.'] * 91
        for cell in Cell:
            piece = self.piece(cell)
            if piece is not None:
                symbols[cell] = piece.fen
        ans = cli.text(symbols)
        return ans
    def turntable(self) -> Self: 
        cls = type(self)
        bitBoards = [None] * 12
        for piece in Piece:
            bitBoards[piece] = self.bitBoard(
                piece.turntable()
            ).turntable()
        ans = cls(*bitBoards)
        return ans
    

Board._setup()