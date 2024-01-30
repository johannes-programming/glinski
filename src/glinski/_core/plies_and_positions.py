# imports
from __future__ import annotations

from string import digits
from typing import Any, Optional, Self, Set, overload

from isometric import Vector
from staticclasses import staticclass

from .bitBoards import *
from .boards import *
from .cells_and_files import *
from .consts import *
from .errors import *
from .pieces import *
from .players import *
from .strangeFuncs import *
from .terminations import *

# __all__
__all__ = ['Ply', 'Position']





# classes

class EMPTY(staticclass):
    pass




class Position:

    # magic methods
    def __eq__(self, other) -> bool:
        cls = type(self)
        if type(other) is not cls:
            return False
        return str(self) == str(other)
    def __hash__(self):
        return str(self).__hash__()
    @overload
    def __init__(self, fen:str):
        ...
    def _init_fen(self, fen:str):
        parts = str(fen).split()
        try:
            return self._init_items(*parts)
        except ValueError:
            raise ValueError(fen)  
    @overload
    def __init__(self,
        board:Board=Board(),
        turn:Player=Player.WHITE,
        ep_cell:Optional[Cell]=None,
        halfmove_clock=0,
        fullmove_number=1,
    ):
        ...
    def _init_items(self,
        board:Board=Board(), 
        turn:Player=Player.WHITE,
        ep_cell:Optional[Cell]=None,
        halfmove_clock=0, 
        fullmove_number=1,
    ):
        return self._init(
            board, turn, ep_cell, 
            halfmove_clock, fullmove_number,
        )
    def __init__(self, *args, **kwargs):
        if (len(args) == 1) and (len(kwargs) == 0):
            if type(args[0]) is not Board:
                return self._init_fen(*args, **kwargs)
        if (len(args) == 0) and (len(kwargs) == 1):
            if set(kwargs.keys()) == {'fen'}:
                return self._init_fen(*args, **kwargs)
        return self._init_items(*args, **kwargs)
    def _init(self,
        board:Board,
        turn:Player,
        ep_cell:Optional[Cell],
        halfmove_clock:int,
        fullmove_number:int,
        /, 
    ):
        # properties
        self._board = Board(board)
        self._turn = self._calc_turn(turn)
        self._halfmove_clock = self._calc_halfmove_clock(
            halfmove_clock
        )
        self._fullmove_number = self._calc_fullmove_number(
            fullmove_number
        )
        self._ep_cell = self._calc_ep_cell(ep_cell)
        self._fen = self._calc_fen()
        # const methods
        self._is_illegal_check = self.board.is_check(
            turn=self.turn.turntable()
        )
        self._is_legal_check = self.board.is_check(
            turn=self.turn
        )
        self._is_legal = self._calc_is_legal()
        # prn
        self._prn_legal_plies = EMPTY
        self._prn_pseudolegal_plies = EMPTY
        self._prn_semilegal_plies = EMPTY
        self._prn_termination = EMPTY
        self._prn_turntable = EMPTY
    def __repr__(self):
        return self.fen
    def __str__(self):
        return self.fen
    

    # calc
    def _calc_ep_cell(self, e, /):
        if e is None:
            e = None
        elif issubclass(type(e), int):
            e = Cell(e)
        else:
            e = Cell.by_fen(e)
        if e is None:
            return None
        if self.board.piece(e) is not None:
            return None
        if not (e.flag & consts.bitBoards.eps[self.turn]):
            return None
        attacker = Piece(self.turn * 6)
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
        for steps in (2, 4):
            hand = walk.rotate(steps)
            hideout = e.apply(hand)
            if self.board.piece(hideout) == attacker:
                return e  
        return None  
    def _calc_fen(self):
        parts = []
        parts.append(self.board.fen)
        parts.append(self.turn.fen)
        if self.ep_cell is None:
            parts.append('-')
        else:
            parts.append(self.ep_cell.fen)
        parts.append(self.halfmove_clock)
        parts.append(self.fullmove_number)
        parts = [str(x) for x in parts]
        ans = ' '.join(parts)
        return ans
    def _calc_fullmove_number(self, value, /):
        ans = int(value)
        if ans < 1:
            raise ValueError(value)
        return ans
    def _calc_halfmove_clock(self, value, /):
        ans = int(value)
        if not (0 <= ans <= 150):
            raise ValueError(value)
        return ans
    def _calc_is_legal(self) -> bool:
        if self.is_illegal_check():
            return False
        if self.board.is_illegal_king():
            return False
        if self.board.is_illegal_pawn():
            return False
        if self.ep_cell is None:
            return True
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
        ep_origin = self.ep_cell.apply(walk)
        ep_killzone = self.ep_cell.apply(-walk)
        ep_victim = Piece(self.turn.turntable() * 6)
        if self.board.piece(ep_origin) is not None:
            return False
        if self.board.piece(ep_killzone) != ep_victim:
            return False
        return True
    def _calc_legal_plies(self) -> Set[Ply]:
        if self.halfmove_clock >= 150:
            return set()
        return self._semilegal_plies()
    def _calc_pseudolegal_plies(self) -> Set[Ply]:
        ucis = {"0000"}
        for c in Cell:
            ucis |= self._pseudolegal_ucis(from_cell=c)
        return {
            Ply(before=self, uci=uci) 
            for uci in ucis
        }
    def _calc_semilegal_plies(self) -> Set[Ply]:
        return {
            p for p in self.pseudolegal_plies()
            if (p.uci and not p.after().is_illegal_check())
        }
    def _calc_termination(self) -> Termination:
        if len(self._semilegal_plies()):
            if self.is_legal_check():
                kind = Termination.Kind.CHECKMATE
            else:
                kind = Termination.Kind.STALEMATE
        else:
            if self.halfmove_clock >= 150:
                kind = Termination.Kind.SEVENTYFIVE_MOVES
            else:
                return None
        return Termination(kind=kind, subject=~self.turn)
    def _calc_turn(self, turn):
        if issubclass(type(turn), int):
            return Player(turn)
        else:
            return Player.by_fen(turn)
    def _calc_turntable(self):
        cls = type(self)
        if self.ep_cell is None:
            ep_cell = None
        else:
            ep_cell = self.ep_cell.turntable()
        ans = cls(
            board=self.board.turntable(),
            turn=self.turn.turntable(),
            ep_cell=ep_cell,
            halfmove_clock=self.halfmove_clock,
            fullmove_number=self.fullmove_number,
        )
        return ans
    

    # more protected methods
    def _pawn_walk_cells(self, from_cell:Cell):
        cls = type(self)
        if from_cell.flag & cls._PROMOTING[self.turn]:
            return BitBoard(0)
        if self.turn == Player.WHITE:
            one_ahead = Cell(from_cell + 1)
        else:
            one_ahead = Cell(from_cell - 1)
        if one_ahead.flag & self.board.occupied():
            return BitBoard(0)
        if from_cell.native() != self.turn * 6:
            return BitBoard(one_ahead.flag)
        if self.turn == Player.WHITE:
            one_ahead = Cell(from_cell + 1)
        else:
            one_ahead = Cell(from_cell - 1)
        
    def _pseudolegal_ucis(self, from_cell:Cell):
        cls = type(self)
        p = self.board.piece(from_cell)
        if p is None:
            return set()
        if p.player != self.turn:
            return set()
        attacks = self.board.attacks(cell=from_cell, piece=p)
        attacks &= ~self.board.occupied(self.turn)
        if p.kind != Piece.Kind.PAWN:
            return {
                (from_cell.uci + a.uci) 
                for a in attacks.cells
            }
        targets = self.board.occupied(~self.turn) | self.ep_bitBoard()
        attacks &= targets
        walks = self.board.occupied().walks(from_cell, p)
        goals = attacks | walks
        to_cells = goals.cells
        ans = set()
        for a in to_cells:
            if a.flag & cls._PROMOTING[self.turn]:
                for p in "nbrq":
                    ans.add(from_cell.uci + a.uci + p)
            else:
                ans.add(from_cell.uci + a.uci)
        return ans
    @classmethod
    def _setup(cls):
        #
        cls._NATIVE = cls(Board.native())
        #
        black_promoting = BitBoard(0)
        for file in File:
            black_promoting |= file[1].flag
        promoting = [None] * 2
        promoting[Player.WHITE] = ~black_promoting
        promoting[Player.BLACK] = black_promoting
        promoting = tuple(promoting)
        cls._PROMOTING = promoting
        #
        walking_P = list()
        for c in range(91):
            cell = Cell(c)
            if promoting[Player.WHITE] & cell.flag:
                steps = []
            elif cell.native() == Piece.P:
                steps = [1, 2]
            else:
                steps = [1]
            cells = set()
            for s in steps:
                cells.add(Cell(c + s))
            bb = BitBoard.by_cells(cells)
            walking_P.append(bb)
        walking_P = tuple(walking_P)
        walking_p = list()
        for c in range(91):
            cell = Cell(c).turntable()
            walking_p.append(walking_P[cell].turntable())
        walking_p = tuple(walking_p)
        walking_PAWN = [None] * 2
        

    
        
            






    # prn 
    def _semilegal_plies(self) -> Set[Ply]:
        if self._prn_semilegal_plies is EMPTY:
            self._prn_semilegal_plies = self._calc_semilegal_plies()
        return set(self._prn_semilegal_plies)
    def legal_plies(self) -> Set[Ply]:
        if self._prn_legal_plies is EMPTY:
            self._prn_legal_plies = self._calc_legal_plies()
        return set(self._prn_legal_plies)
    def pseudolegal_plies(self) -> Set[Ply]:
        if self._prn_pseudolegal_plies is EMPTY:
            self._prn_pseudolegal_plies = self._calc_pseudolegal_plies()
        return set(self._prn_pseudolegal_plies)
    def termination(self) -> Termination:
        if self._prn_termination is EMPTY:
            self._prn_termination = self._calc_termination()
        return self._prn_termination
    def turntable(self):
        if self._prn_turntable is EMPTY:
            self._prn_turntable = self._calc_turntable()
        return self._prn_turntable

    # core properties
    @property
    def board(self):
        return self._board
    @property
    def turn(self):
        return self._turn
    @property
    def ep_cell(self):
        return self._ep_cell
    @property
    def halfmove_clock(self):
        return self._halfmove_clock
    @property
    def fullmove_number(self):
        return self._fullmove_number
    @property
    def fen(self):
        return self._fen


    # boolean methods
    def is_checkmate(self) -> bool: 
        if self.termination() is None:
            return False
        if self.termination().kind != Termination.Kind.CHECKMATE:
            return False
        return True
    def is_illegal_check(self) -> bool:
        return self._is_illegal_check
    def is_legal(self) -> bool:
        return self._is_legal
    def is_legal_check(self) -> bool:
        return self._is_legal_check
    def is_repetition(self, other:Position):
        if type(other) is not Position:
            raise TypeError(other)
        if self.board != other.board:
            return False
        if self.turn != other.turn:
            return False
        if self.ep_cell != other.ep_cell:
            return False
        return True
    def is_stalemate(self) -> bool: 
        if self.termination() is None:
            return False
        if self.termination().kind != Termination.Kind.STALEMATE:
            return False
        return True


    # other public methods
    def ep_bitBoard(self) -> BitBoard:
        if self.ep_cell is None:
            return BitBoard(0)
        return BitBoard(self.ep_cell.flag)
    @classmethod
    def native(cls):
        return cls._NATIVE


Position._setup()






















class Ply:
    class UCI:
        # magic methods
        def __bool__(self):
            return self._string != "0000"
        def __eq__(self, other: Any) -> bool:
            cls = type(self)
            if type(other) is not cls:
                return False
            return str(self) == str(other)
        def __hash__(self) -> int:
            return str(self).__hash__()
        @overload
        def __init__(self):
            ...
        def _init_null(self):
            self._init('0000', Cell.a1, Cell.a1, None)
        @overload
        def __init__(self, string:str, /):
            ...
        def _init_str(self, string:str, /):
            s = str(string).lower()
            i = 3 if (s[2] in digits) else 2
            j = len(s) if (s[-1] in digits) else -1
            p = Piece.Kind.by_uci(s[j:], allow_empty=True)
            self._init(s, Cell[s[:i]], Cell[s[i:j]], p)
        @overload
        def __init__(self,
            from_cell:Cell,
            to_cell:Cell,
            promotion:Optional[Piece.Kind]=None,
        ):
            ...
        def _init_items(self,
            from_cell:Cell,
            to_cell:Cell,
            promotion:Optional[Piece.Kind]=None,
        ):
            from_cell = Cell(from_cell)
            s = from_cell.uci
            to_cell = Cell(to_cell)
            s += to_cell.uci
            if promotion is not None:
                promotion = Piece.Kind(promotion)
                s += promotion.uci
            if s == 'a1a1':
                s = '0000'
            self._init(s, from_cell, to_cell, promotion)
        def __init__(self, *args, **kwargs):
            if len(kwargs):
                self._init_items(*args, **kwargs)
            elif len(args) >= 2:
                self._init_items(*args)
            elif len(args) == 0:
                self._init_null()
            elif set(args[0]) == {'0'}:
                self._init_null()
            else:
                self._init_str(*args)
        def _init(self,
            string:str, 
            from_cell:Cell,
            to_cell:Cell,
            promotion:Optional[Piece.Kind],
            /,
        ):
            self._from_cell = from_cell
            self._to_cell = to_cell
            self._promotion = promotion
            self._string = string
        def __repr__(self):
            return "Ply.UCI('%s')" % str(self)
        def __str__(self) -> str:
            return self._string
        # public methods
        def turntable(self):
            cls = type(self)
            ans = cls(
                self.from_cell.turntable(),
                self.to_cell.turntable(),
                self.promotion,
            )
            return ans
        # properties
        @property
        def from_cell(self) -> Cell:
            return self._from_cell
        @property
        def to_cell(self) -> Cell:
            return self._to_cell
        @property
        def promotion(self) -> Optional[Piece.Kind]:
            return self._promotion

    # magic methods
    def __bool__(self):
        return bool(self.uci)
    def __eq__(self, other):
        cls = type(self)
        if type(other) is not cls:
            return False
        if self.before != other.before:
            return False
        if self.uci != other.uci:
            return False
        return True
    def __hash__(self) -> int:
        return str(self).__hash__()
    def __init__(self, *,
        before:Position, 
        uci:Ply.UCI="0000",
    ):
        # 
        self._before = Position(before)
        self._uci = Ply.UCI(uci)
        # 
        self._piece = self._calc_piece()
        self._is_zeroing = self._calc_is_zeroing()
        self._vector = self._calc_vector()
        self._digest = self.vector().digest()
        self._order, self._unit = self._calc_factorize()
        self._capture = self._calc_capture()
        self._after = self._calc_after()
        #
        self._check()
    def __str__(self):
        cls = type(self)
        ans = "{0}(before='{1}', uci='{2}')".format(
            cls.__name__,
            self.before,
            self.uci,
        )
        return ans


    # calc
    def _calc_after(self):
        # board
        mut = dict()
        if self.uci:
            mut[self.uci.from_cell] = None
        if self.uci.promotion is None:
            mut[self.uci.to_cell] = self.before.board.piece(self.uci.from_cell)
        else:
            mut[self.uci.to_cell] = Piece(6 * self.before.turn + self.uci.promotion)
        ep_killzone = self._calc_ep_killzone()
        if ep_killzone is not None:
            mut[ep_killzone] = None
        b = self.before.board.apply(mut)
        # turn 
        t = self.before.turn.turntable()
        # ep_cell
        if not self.uci:
            e = '-'
        elif self.piece().kind != Piece.Kind.PAWN:
            e = '-'
        elif self._order != 2:
            e = '-'
        else:
            e = self.uci.from_cell.apply(self._unit).uci
        # halfmove_clock
        h = 0 if self.is_zeroing() else (self.before.halfmove_clock + 1)
        # fullmove_number
        is_blacks_turn = self.before.turn == Player.BLACK
        f = self.before.fullmove_number + is_blacks_turn
        ans = Position(
            board=b, 
            turn=t, 
            ep_cell=e, 
            halfmove_clock=h, 
            fullmove_number=f,
        )
        return ans
    def _calc_capture(self):
        if not self.uci:
            return None
        ans = self.before.board.piece(self.uci.to_cell)
        if ans is not None:
            return ans
        if self.is_ep:
            return self.piece().turntable()
        return None
    def _calc_ep_killzone(self):
        if self.before.ep_cell is None:
            return None
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[
            self.before.turn
        ]
        try:
            return self.before.ep_cell.apply(-walk)
        except:
            return None
    def _calc_factorize(self):
        if self.vector():
            return self.vector().factorize()
        return 0, self.vector()
    def _calc_is_zeroing(self):
        if not self.uci:
            return False
        elif self.piece().kind == Piece.Kind.PAWN:
            return True
        elif self.before.board.piece(self.uci.to_cell) is None:
            return False
        else:
            return True
    def _calc_piece(self):
        if not self.uci:
            return None
        return self.before.board.piece(
            self.uci.from_cell
        )
    def _calc_vector(self):
        return self.uci.from_cell.vector_to(
            self.uci.to_cell
        )


    # 
    def _check(self):
        if not self.uci:
            return 
        if self.uci.from_cell == self.uci.to_cell:
            raise NotPseudolegalError
        if self.piece() is None:
            raise NotPseudolegalError
        if self.piece().player != self.before.turn:
            raise NotPseudolegalError
        promotion_bb = consts.bitBoards.promotions[self.before.turn]
        if self.piece().kind != Piece.Kind.PAWN:
            promotion_needed = False
        elif self.uci.to_cell.flag & promotion_bb:
            promotion_needed = True
        else:
            promotion_needed = False
        if promotion_needed != self.is_promotion():
            raise NotPseudolegalError
        c = self.uci.from_cell
        while True:
            c = c.apply(self._unit)
            if c == self.uci.to_cell:
                break
            if self.before.board.piece(c) is not None:
                raise NotPseudolegalError
        # 
        unit_abs = float(abs(self._unit))
        if self.piece().kind == Piece.Kind.PAWN:
            if unit_abs != 1 ** .5:
                raise NotPseudolegalError
            if self._order > 2:
                raise NotPseudolegalError
            is_forward = self._digest.y > 0
            is_white = self.before.turn == Player.WHITE
            if is_white != is_forward:
                raise NotPseudolegalError
            target = self.before.board.piece(self.uci.to_cell)
            is_sideways = self._digest.x != 0
            if (not is_sideways) and (target is not None):
                raise NotPseudolegalError
            if is_sideways and (self._order == 2):
                raise NotPseudolegalError
            not_to_ep_cell = self.uci.to_cell != self.before.ep_cell
            if is_sideways and (target is None) and not_to_ep_cell:
                raise NotPseudolegalError
        if self.piece().kind == Piece.Kind.KNIGHT:
            if unit_abs != 7 ** .5:
                raise NotPseudolegalError
            if self._order != 1:
                raise NotPseudolegalError
        if self.piece().kind == Piece.Kind.BISHOP:
            if unit_abs != 3 ** .5:
                raise NotPseudolegalError
        if self.piece().kind == Piece.Kind.ROOK:
            if unit_abs != 1 ** .5:
                raise NotPseudolegalError
        if self.piece().kind == Piece.Kind.QUEEN:
            if unit_abs not in {1 ** .5, 3 ** .5}:
                raise NotPseudolegalError
        if self.piece().kind == Piece.Kind.KING:
            if unit_abs not in {1 ** .5, 3 ** .5}:
                raise NotPseudolegalError
            if self._order != 1:
                raise NotPseudolegalError


    # core properties
    @property
    def before(self) -> Position:
        return self._before
    @property
    def uci(self) -> Ply.UCI:
        return self._uci
    

    # boolean methods
    def is_ep(self) -> bool:
        if self.before.ep_cell != self.uci.to_cell:
            return False
        if self.piece().kind != Piece.Kind.PAWN:
            return False
        if self._digest.x == 0:
            return False
        return True
    def is_legal(self) -> bool:
        if self.before.termination() is not None:
            return False
        if self.after().is_illegal_check():
            return False
        return True
    def is_promotion(self) -> bool:
        return self.uci.promotion is not None
    def is_zeroing(self) -> bool:
        return self._is_zeroing
    

    # other public methods
    def after(self) -> Position:
        return self._after
    def capture(self) -> Optional[Piece]:
        return self._capture
    def piece(self) -> Piece:
        return self._piece
    def turntable(self) -> Self:
        cls = type(self)
        ans = cls(
            before=self.before.turntable(),
            uci=self.uci.turntable(),
        )
        return ans
    def vector(self) -> Vector:
        return self._vector







