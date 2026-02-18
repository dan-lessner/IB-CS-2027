from AbstractSet import AbstractSet, BuiltInSet


class CuckooHashSet(AbstractSet):
    def __init__(self, initial_capacity=11):
        self._capacity = initial_capacity
        self.table1 = [None] * self._capacity
        self.table2 = [None] * self._capacity
        self._size = 0

    def _h1(self, element):
        return hash((element, 1)) % self._capacity

    def _h2(self, element):
        return hash((element, 2)) % self._capacity

    def contains(self, element):
        i1 = self._h1(element)
        if self.table1[i1] == element:
            return True
        i2 = self._h2(element)
        if self.table2[i2] == element:
            return True
        return False

    def add(self, element):
        if self.contains(element):
            return

        if self._size + 1 > self._capacity * 0.5:
            self._resize(self._capacity * 2)

        cur = element
        table = 1
        max_kicks = max(50, self._capacity * 2)

        for _ in range(max_kicks):
            if table == 1:
                i = self._h1(cur)
                if self.table1[i] is None:
                    self.table1[i] = cur
                    self._size += 1
                    return
                # kick out
                cur, self.table1[i] = self.table1[i], cur
                table = 2
            else:
                i = self._h2(cur)
                if self.table2[i] is None:
                    self.table2[i] = cur
                    self._size += 1
                    return
                cur, self.table2[i] = self.table2[i], cur
                table = 1

        self._resize(self._capacity * 2)
        self.add(element)

    def remove(self, element):
        i1 = self._h1(element)
        if self.table1[i1] == element:
            self.table1[i1] = None
            self._size -= 1
            return
        i2 = self._h2(element)
        if self.table2[i2] == element:
            self.table2[i2] = None
            self._size -= 1
            return

    def size(self):
        return self._size

    def elements(self):
        for x in self.table1:
            if x is not None:
                yield x
        for x in self.table2:
            if x is not None:
                yield x

    def __iter__(self):
        return self.elements()

    def union(self, other):
        result = BuiltInSet()
        for x in self:
            result.add(x)
        for x in other:
            result.add(x)
        return result

    def intersection(self, other):
        result = BuiltInSet()
        for x in self:
            if other.contains(x):
                result.add(x)
        return result

    def _resize(self, new_capacity):
        old_items = list(self.elements())
        self._capacity = max(3, int(new_capacity))
        self.table1 = [None] * self._capacity
        self.table2 = [None] * self._capacity
        self._size = 0
        for x in old_items:
            self.add(x)