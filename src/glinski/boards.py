from isometric import Vector

_white_pieces = "KQRBNP"
_spot = '·'#chr(183)

class _Empty:
    pass
class Board:
    def __init__(self):
        self._pieces = {position: _spot for position in self.positions()}
    def __str__(self):
        lines = [([" "] * 31) for a in range(21)]
        for position, piece in self.pieces():
            p, q = position
            x = 15 + 3 * (q - p)
            y = 10 - p - q
            lines[y][x] = piece
        lines = ["".join(line) for line in lines]
        ans = '\n'.join(lines)
        return ans
    def __len__(self):
        return len(self.positions())
    def __contains__(self, value):
        value = self.piece(value)
        return value in self._pieces.values()
    def __getitem__(self, key):
        position = self._vector(key)
        piece = self._pieces[position]
        return piece
    def __setitem__(self, key, value):
        position = self.position(key)
        piece = self.piece(value)
        self._pieces[position] = piece
    def __delitem__(self, key):
        position = self.position(key)
        self._pieces[position] = _spot
    def get(self, key, /, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    @classmethod
    def spot(cls):
        return _spot
    @classmethod
    def positions(cls):
        ans = set()
        for p in range(-5, 6):
            for q in range(-5, 6):
                if abs(p - q) < 6:
                    ans.add(Vector(p, q))
        return ans
    @classmethod
    def vector(cls, objA, objB=_Empty, /):
        if objB is _Empty:
            return cls._vector(objA)
        else:
            return cls._vector(objB) - cls._vector(objA)
    @classmethod
    def _vector(cls, obj, /):
        try:
            return Vector(obj)
        except:
            pass
        obj = str(obj)
        s = "abcdefghikl".index(obj[0]) - 5
        t = int(obj[1:]) - 6
        p = t + max(0, -s)
        q = t + max(0, s)
        vector = Vector(p, q)
        if vector not in cls.positions():
            raise ValueError(f"'{obj}' is not a position. ")
        return vector
    @classmethod
    def position(cls, obj, /):
        ans = cls._vector(obj)
        if ans not in cls.positions():
            raise ValueError
        return ans
    @classmethod
    def name(cls, obj, /):
        position = cls.position(obj)
        p, q = position
        s = q - p
        t = min(p, q)
        return "abcdefghikl"[s] + str(t + 6)
    @classmethod
    def bg(cls, obj, /):
        position = cls.position(obj)
        index = sum(position) % 3
        return ['grey', 'black', 'white'][index]
    @classmethod
    def piece(cls, value, /):
        if type(value) is not str:
            raise TypeError
        if len(value) != 1:
            raise ValueError
        if value == _spot:
            return value
        if value.upper() in _white_pieces:
            return value
        raise ValueError
    @classmethod
    def pawnstarts(cls, /, white):
        names = [(c + "7") for c in "bcdefghik"]
        ans = [cls._vector(n) for n in names]
        if white:
            ans = [v.flip_horizontally() for v in ans]
        return ans
    @classmethod
    def pawngoals(cls, /, white):
        names = [(c + "1") for c in "abcdefghikl"]
        ans = [cls._vector(n) for n in names]
        if not white:
            ans = [v.flip_horizontally() for v in ans]
        return ans
    def all_positions(self, *pieces):
        ans = set()
        for position, piece in self._pieces.items():
            if piece in pieces:
                ans.add(position)
        return ans
    def reposition(self, oldposition, newposition):
        ans = self[newposition]
        self[newposition] = self[oldposition]
        del self[oldposition]
        return ans
    def pieces(self):
        return set(self._pieces.items())
    def clone(self):
        ans = Board()
        for position, piece in self.pieces():
            ans[position] = piece
        return ans
    def clear(self):
        for position in self.positions():
            del self[position]
    def setup(self):
        self.clear()
        # pawns
        for start in self.pawnstarts(white=False)
            self[start] = "p"
        # knights
        self["d9"] = "n"
        self["h9"] = "n"
        # bishops
        self["f9"] = "b"
        self["f10"] = "b"
        self["f11"] = "b"
        # rocks
        self["c8"] = "r"
        self["i8"] = "r"
        # queen
        self["e10"] = "q"
        # king
        self["g10"] = "k"

        for position in self.positions():
            if sum(position) <= 0:
                continue
            piece = self[position]
            if piece == _spot:
                continue
            self[position.flip_horizontally()] = piece.swapcase()
    def mirror(self):
        for position in self.positions():
            if sum(position) < 0:
                continue
            piece = self[position].swapcase()
            if sum(position) == 0:
                self[position] = piece
                continue
            antiposition = position.flip_horizontally()
            self[position] = self[antiposition].swapcase()
            self[antiposition] = piece

        
        

