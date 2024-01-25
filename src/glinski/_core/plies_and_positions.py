# imports
from __future__ import annotations

import typing
from string import digits

from isometric import Vector

from .bitBoards import *
from .boards import *
from .cells_and_files import *
from .consts import *
from .errors import *
from .pieces import *
from .players import *
from .terminations import *

# __all__
__all__ = ['Ply', 'Position']





# 
class Position:
    # dunder
    def __eq__(self, other) -> bool:
        cls = type(self)
        if type(other) is not cls:
            return False
        return str(self) == str(other)
    def __getattr__(self, key:str):
        forbidden = {'__', '_calc', '_setup'}
        if any(key.startswith(x) for x in forbidden):
            raise AttributeError(key)
        elif key.startswith('_'):
            func = getattr(self, "_calc" + key)
            ans = func()
            setattr(self, key, ans)
            return ans
        else:
            return getattr(self, '_' + key)
    def __hash__(self):
        return str(self).__hash__()
    def __init__(self, 
        string:typing.Optional[str]=None, /,
    ):
        # 
        if string is not None:
            (b, t, e, h, f) = str(string).split()
        else:
            b = "1/3/5/7/9/11/11/11/11/11/11"
            t = 'w'
            e = '-'
            h = '0'
            f = '1'
        # board
        self._board = Board.by_fen(b)
        # turn
        self._turn = Player.by_fen(t)
        # halfmove_clock
        self._halfmove_clock = int(h)
        if self.halfmove_clock < 0:
            raise ValueError(self.halfmove_clock)
        # fullmove_number
        self._fullmove_number = int(f)
        if self.fullmove_number < 1:
            raise ValueError(self.fullmove_number)
        # ep_cell
        self._ep_cell = self.__ep_cell(e)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __str__(self):
        return self.fen



    # hidden
    def __ep_cell(self, e, /):
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
    def __pseudolegal_ucis(self, from_cell:Cell):
        p = self.board.piece(from_cell)
        if p is None:
            return set()
        if p.player != self.turn:
            return set()
        attacks = self.board.attacks(cell=from_cell, piece=p).cells
        if p.kind != Piece.Kind.PAWN:
            return {from_cell + a.name for a in attacks}
        pawn_to_cells = set()
        for a in attacks:
            if self.board.piece(a) is not None:
                pawn_to_cells.add(a)
            if a == self.ep_cell:
                pawn_to_cells.add(a)
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
        for order in range(1, 3):
            try:
                a = from_cell.apply(walk * order)
            except:
                break
            if self.board.piece(a) is not None:
                break
            pawn_to_cells.add(a)
            if from_cell.native() != p:
                break
        ans = set()
        for a in pawn_to_cells:
            if a.flag & consts.bitBoards.promotions[self.turn]:
                for p in "nbrq":
                    ans.add(from_cell.name + a.name + p)
            else:
                ans.add(from_cell.name + a.name)
        return ans
    def __termination_kind(self) -> Termination.Kind:
        check_everywhere = all(
            (ply.uci and ply.after.is_illegal_check)
            for ply in self.pseudolegal_plies
        )
        if check_everywhere:
            if self.is_legal_check:
                return Termination.Kind.CHECKMATE
            else:
                return Termination.Kind.STALEMATE
        else:
            if self.halfmove_clock >= 150:
                return Termination.Kind.SEVENTYFIVE_MOVES
            else:
                return None
    

    


    # calc
    def _calc_ep_bitBoard(self) -> BitBoard:
        if self.ep_cell is None:
            n = 0
        else:
            n = self.ep_cell.flag
        ans = BitBoard(n)
        return ans
    def _calc_fen(self) -> str:
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
    def _calc_is_checkmate(self) -> bool: 
        if self.termination is None:
            return False
        if self.termination.kind != Termination.Kind.CHECKMATE:
            return False
        return True
    def _calc_is_illegal_check(self) -> bool: 
        return self.board.is_check(turn=self.turn.opponent())
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
        ep_victim = Piece(self.turn.opponent() * 6)
        if self.board.piece(ep_origin) is not None:
            return False
        if self.board.piece(ep_killzone) != ep_victim:
            return False
        return True
    def _calc_is_legal_check(self) -> bool: 
        return self.board.is_check(turn=self.turn)
    def _calc_is_stalemate(self) -> bool: 
        if self.termination is None:
            return False
        if self.termination.kind != Termination.Kind.STALEMATE:
            return False
        return True
    def _calc_legal_plies(self):
        if self.halfmove_clock >= 150:
            return set()
        return {
            p for p in self.pseudolegal_plies
            if p.uci if (not p.after.is_illegal_check)
        }
    def _calc_pseudolegal_plies(self):
        commands = {"0000"}
        for c in Cell:
            commands |= self.__pseudolegal_ucis(from_cell=c)
        ans = {Ply(before=self, uci=s) for s in commands}
        return ans
    def _calc_termination(self):
        kind = self.__termination_kind()
        if kind is None:
            return None
        return Termination(
            kind=kind,
            subject=self.turn.opponent,
        )
    

    #
    @classmethod
    def _setup(cls):
        native_fen = Board.native().fen + " w - 0 1" 
        cls._NATIVE = cls(native_fen)


    #
    @classmethod
    def by_fen(cls, value, /):
        return cls(value)
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
    @classmethod
    def native(cls):
        return cls._NATIVE
Position._setup()







class Ply:
    class UCI:
        # dunder
        def __bool__(self):
            return self._string != "0000"
        def __eq__(self, other: typing.Any) -> bool:
            cls = type(self)
            if type(other) is not cls:
                return False
            return str(self) == str(other)
        def __hash__(self) -> int:
            return str(self).__hash__()
        def __init__(self, *, string:str="0000") -> None:
            s = str(string).lower()
            s = "a1a1" if s == "0000" else s
            i = 3 if s[2] in digits else 3
            j = None if s[-1] in digits else -1
            self._from_cell = Cell[s[:i]]
            self._to_cell = Cell[s[i:j]]
            self._promotion = Piece.Kind.by_uci(s[j:], allow_empty=True)
            self._string = "0000" if (s == "a1a1") else s
        def __ne__(self, other: typing.Any) -> bool:
            return not (self == other)
        def __str__(self) -> str:
            return self._string

        # properties
        @property
        def from_cell(self) -> Cell:
            return self._from_cell
        @property
        def to_cell(self) -> Cell:
            return self._to_cell
        @property
        def promotion(self) -> typing.Optional[Piece.Kind]:
            return self._promotion

    #  
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
    def __getattr__(self, key):
        forbidden = {'__', '_calc', '_setup'}
        if any(key.startswith(x) for x in forbidden):
            raise AttributeError(key)
        if not key.startswith('_'):
            return getattr(self, '_' + key)
        func = getattr(self, "_calc" + key)
        ans = func()
        setattr(self, key, ans)
        return ans
    def __hash__(self) -> int:
        return str(self).__hash__()
    def __init__(self, *,
        before:Position, 
        uci:Ply.UCI="0000",
    ):
        self._before = Position(before)
        self._uci = Ply.UCI(uci)
        self.__check()
    def __ne__(self, other):
        return not self.__eq__(other)


    #   
    def __check(self):
        if not self.uci:
            return 
        if self.uci.from_cell == self.uci.to_cell:
            raise NotPseudolegalError
        if self.piece is None:
            raise NotPseudolegalError
        if self.piece.player != self.before.turn:
            raise NotPseudolegalError
        promotion_bb = consts.bitBoards.promotions[self.before.turn]
        if self.piece.kind != Piece.Kind.PAWN:
            promotion_needed = False
        elif self.uci.to_cell.flag & promotion_bb:
            promotion_needed = True
        else:
            promotion_needed = False
        if promotion_needed != self.is_promotion:
            raise NotPseudolegalError
        c = self.from_cell
        while True:
            c = c.apply(self.unit)
            if c == self.to_cell:
                break
            if self.board.piece(c) is not None:
                raise NotPseudolegalError
        # 
        unit_abs = float(abs(self.unit))
        if self.piece.kind == Piece.Kind.PAWN:
            if unit_abs != 1 ** .5:
                raise NotPseudolegalError
            if self.order > 2:
                raise NotPseudolegalError
            is_forward = self.unit.digest().y > 0
            is_white = self.before.turn == Player.WHITE
            if is_white != is_forward:
                raise NotPseudolegalError
            target = self.before.board.piece(self.uci.to_cell)
            is_sideways = self.unit.digest().x != 0
            if (not is_sideways) and (target is not None):
                raise NotPseudolegalError
            if is_sideways and (self.order == 2):
                raise NotPseudolegalError
            not_to_ep_cell = self.uci.to_cell != self.before.ep_cell
            if is_sideways and (target is None) and not_to_ep_cell:
                raise NotPseudolegalError
        if self.piece.kind == Piece.Kind.KNIGHT:
            if unit_abs != 7 ** .5:
                raise NotPseudolegalError
            if self.order != 1:
                raise NotPseudolegalError
        if self.piece.kind == Piece.Kind.BISHOP:
            if unit_abs != 3 ** .5:
                raise NotPseudolegalError
        if self.piece.kind == Piece.Kind.ROOK:
            if unit_abs != 1 ** .5:
                raise NotPseudolegalError
        if self.piece.kind == Piece.Kind.QUEEN:
            if unit_abs not in {1 ** .5, 3 ** .5}:
                raise NotPseudolegalError
        if self.piece.kind == Piece.Kind.KING:
            if unit_abs not in {1 ** .5, 3 ** .5}:
                raise NotPseudolegalError
            if self.order != 1:
                raise NotPseudolegalError
    def __ep_killzone(self):
        if self.before.ep_cell is None:
            return None
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.before.turn]
        try:
            return self.before.ep_cell.apply(-walk)
        except:
            return None




    #
    def _calc_after(self):
        # board
        mut = dict()
        if self.uci:
            mut[self.uci.from_cell] = None
        if self.uci.promotion is None:
            mut[self.uci.to_cell] = self.before.board.piece(self.uci.from_cell)
        else:
            mut[self.uci.to_cell] = Piece(6 * self.before.turn + self.uci.promotion)
        ep_killzone = self.__ep_killzone()
        if ep_killzone is not None:
            mut[ep_killzone] = None
        b = self.before.board.apply(mut).fen
        # turn 
        t = self.before.turn.opponent().fen
        # ep_cell
        if not self.uci:
            e = '-'
        elif self.piece.kind != Piece.Kind.PAWN:
            e = '-'
        elif self.order != 2:
            e = '-'
        else:
            e = self.uci.from_cell.apply(self.unit).name
        # halfmove_clock
        h = 0 if self.is_zeroing else str(self.before.halfmove_clock + 1)
        # fullmove_number
        is_blacks_turn = self.before.turn == Player.BLACK
        f = self.before.fullmove_number + is_blacks_turn
        ans = f"{b} {t} {e} {h} {f}"
        return ans
    def _calc_is_ep(self):
        if self.before.ep_cell != self.uci.to_cell:
            return False
        if self.piece.kind != Piece.Kind.PAWN:
            return False
        if self.unit.digest().x == 0:
            return False
        return True
    def _calc_is_legal(self) -> bool:
        if self.before.termination is not None:
            return False
        if self.after.is_illegal_check:
            return False
        return True
    def _calc_is_null(self) -> bool:
        return not self.uci
    def _calc_is_promotion(self) -> bool:
        return self.uci.promotion is not None
    def _calc_is_zeroing(self) -> bool:
        if not self.uci:
            return False
        if self.piece.kind == Piece.Kind.PAWN:
            return True
        if self.before.board.piece(self.uci.to_cell) is not None:
            return True
        return False
    def _calc_order(self) -> int:
        if self.vector:
            return self.vector.factorize()[0]
        else:
            return 0
    def _calc_piece(self):
        if not self.uci:
            return None
        return self.before.board.piece(self.uci.from_cell)
    def _calc_unit(self):
        if self.vector:
            return self.vector.factorize()[1]
        else:
            return 0
    def _calc_vector(self):
        return self.uci.from_cell.vector_to(self.uci.to_cell)
    







