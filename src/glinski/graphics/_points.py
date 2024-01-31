from typing import NamedTuple, Union, overload, Self, Iterable
from math import isfinite

__all__ = ['Point']


class Point:
    #
    def __abs__(self):
        return (self * self) ** .5
    def __add__(self, other):
        cls = type(self)
        other = cls(other)
        x = self.x + other.x
        y = self.y + other.y
        ans = Point(x, y)
        return ans
    def __bool__(self):
        return any(self)
    def __divmod__(self, other):
        cls = type(self)
        xQ, xR = divmod(self.x, other)
        yQ, yR = divmod(self.y, other)
        q = cls(xQ, yQ)
        r = cls(xR, yR)
        return q, r
    def __eq__(self, other) -> bool:
        cls = type(self)
        try:
            other = cls(other)
        except:
            return False
        return tuple(self) == tuple(other)
    def __floordiv__(self, other):
        return self.__divmod__(other)[0]
    def __getitem__(self, key):
        cls = type(self)
        ans = tuple(self)[key]
        if type(ans) is not tuple:
            return ans
        if len(ans) != 2:
            return ans
        ans = cls(*ans)
        return ans
    def __hash__(self):
        return tuple(self).__hash__()
    @overload
    def __init__(self, 
        x:Union[int, float]=0, 
        y:Union[int, float]=0,
    ) -> None:
        ...
    @overload
    def __init__(self, 
        iterable:Iterable, /,
    ) -> None:
        ...
    def __init__(self, *args, **kwargs):
        if len(kwargs) != 0:
            return self._init(*args, **kwargs)
        if len(args) != 1:
            return self._init(*args)
        try:
            x, y = args[0]
        except:
            self._init(*args)
        else:
            self._init(x, y)
    def _init(self, 
        x:Union[int, float]=0, 
        y:Union[int, float]=0,
    ) -> None:
        self._check_item(x)
        self._check_item(y)
        self._x = x
        self._y = y
    def __invert__(self):
        cls = type(self)
        ans = cls(
            ~self.x,
            ~self.y,
        )
        return ans
    def __iter__(self):
        yield self.x
        yield self.y
    def __mod__(self, other):
        return divmod(self, other)[1]
    def __mul__(self, other):
        cls = type(self)
        try:
            other = cls(other)
        except:
            pass
        if type(other) is cls:
            ans = self.x * other.x
            ans += self.y * other.y
        else:
            x = self.x * other
            y = self.y * other
            ans = Point(x, y)
        return ans
    def __neg__(self) -> Self:
        cls = type(self)
        ans = cls(
            -self.x,
            -self.y,
        )
        return ans
    def __pow__(self, other):
        if type(other) is not int:
            raise TypeError(other)
        if other < 0:
            raise ValueError(other)
        ans = 1
        for i in range(other):
            ans *= self
        return ans
    def __radd__(self, other) -> Self:
        return self.__add__(other)
    def __rmul__(self, other):
        return self.__mul__(other)
    def __rsub__(self, other) -> Self:
        return other + (-self)
    def __sub__(self, other) -> Self:
        return self + (-other)
    def __truediv__(self, other):
        cls = type(self)
        ans = cls(
            self.x / other,
            self.y / other,
        )
        return ans
    #
    @classmethod
    def _check_item(cls, value):
        if type(value) is int:
            return
        if type(value) is not float:
            raise TypeError(value)
        if not isfinite(value):
            raise ValueError(value)
    #
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    #
    def apply(self, func) -> Self:
        cls = type(self)
        ans = cls(
            func(self.x),
            func(self.y),
        )
        return ans
    