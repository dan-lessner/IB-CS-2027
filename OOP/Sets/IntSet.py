from AbstractSet import AbstractSet

'''
Jenda
An int behaves like an array - each bit represents whether a number at that index is in the set or not. We use bit operations to manipulate the set
'''

class IntSet(AbstractSet):
    def __init__(self, num = 0):
        self.num = num

    def add(self, x: int):
        self.num |= 1 << x

    def remove(self, x: int):
        self.num &= ~(1 << x)

    def discard(self, x: int):
        self.num &= ~(1 << x)

    def contains(self, x: int) -> bool:
        return (self.num & (1 << x)) != 0

    def union(self, other):
        return IntSet(self.num | other.num)

    def intersection(self, other):
        return IntSet(self.num & other.num)

    def difference(self, other):
        return IntSet(self.num & ~other.num)

    def issubset(self, other):
        return (self.num & other.num) == self.num

    def size(self) -> int:
        return self.num.bit_count()

    def elements(self):
        n = self.num
        bit_position = 0
        while n:
            if n & 1:
                yield bit_position
            n >>= 1
            bit_position += 1

    def __repr__(self):
        return "{" + ", ".join(str(x) for x in self) + "}"