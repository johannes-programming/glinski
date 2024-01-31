

class Color:
    
    @classmethod
    def _setup(cls):
        cls.__new__ = strangeFuncs.IntModNew(cls.__new__, 256 ** 4)