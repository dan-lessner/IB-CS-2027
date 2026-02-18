from AbstractSet import AbstractSet, BuiltInSet


class SimpleHashSet(AbstractSet):
    def __init__(self, capacity=11):
        self._capacity = capacity
        self.buckets = [[] for _ in range(self._capacity)]
        self._size = 0

    def _bucket_index(self, element):
        return hash(element) % self._capacity

    def add(self, element):
        b = self.buckets[self._bucket_index(element)]
        if element in b:
            return
        b.append(element)
        self._size += 1
        if self._size > self._capacity:
            self._resize(self._capacity * 2)

    def remove(self, element):
        b = self.buckets[self._bucket_index(element)]
        b.remove(element)
        self._size -= 1

    def contains(self, element):
        return element in self.buckets[self._bucket_index(element)]

    def size(self):
        return self._size

    def elements(self):
        for b in self.buckets:
            for x in b:
                yield x

    def __iter__(self):
        return self.elements()

    def union(self, other):
        for x in other:
            self.add(x)
        return self

    def intersection(self, other):
        result = BuiltInSet()
        for x in self:
            if other.contains(x):
                result.add(x)
        return result

    def _resize(self, new_capacity):
        old = list(self.elements())
        self._capacity = int(new_capacity)
        self.buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for x in old:
            self.add(x)