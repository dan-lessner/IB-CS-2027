from AbstractSet import AbstractSet


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
        return set(self)

    def __iter__(self):
        n = self.num
        bit_position = 0
        while n:
            if n & 1:
                yield bit_position
            n >>= 1
            bit_position += 1

    def __repr__(self):
        return "{" + ", ".join(str(x) for x in self) + "}"

import random
import time

# Parameters
N = 1_000_000
RANGE = 2_000_000

set1_elements = random.sample(range(RANGE), N)
set2_elements = random.sample(range(RANGE), N)

start = time.time()
set1 = IntSet()
for x in set1_elements:
    set1.add(x)
end = time.time()
print(f"Set1 insertion: {end - start:.2f} seconds")

start = time.time()
set2 = IntSet()
for x in set2_elements:
    set2.add(x)
end = time.time()
print(f"Set2 insertion: {end - start:.2f} seconds")

check_elements = random.sample(set1_elements, 1000) + random.sample(range(RANGE), 1000)
random.shuffle(check_elements)
start = time.time()
results = [set1.contains(x) for x in check_elements]
end = time.time()
print(f"Set1 contains (2000 checks): {end - start:.4f} seconds")

start = time.time()
union_set = set1.union(set2)
end = time.time()
print(f"Union: {end - start:.2f} seconds")

start = time.time()
intersection_set = set1.intersection(set2)
end = time.time()
print(f"Intersection: {end - start:.2f} seconds")

start = time.time()
difference_set = set1.difference(set2)
end = time.time()
print(f"Difference: {end - start:.2f} seconds")

start = time.time()
issub = set1.issubset(set2)
end = time.time()
print(f"issubset: {end - start:.4f} seconds (result: {issub})")

remove_elements = random.sample(set1_elements, 1000)
start = time.time()
for x in remove_elements:
    set1.remove(x)
end = time.time()
print(f"Set1 removal (1000 elements): {end - start:.4f} seconds")