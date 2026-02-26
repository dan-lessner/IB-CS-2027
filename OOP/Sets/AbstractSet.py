from abc import ABC, abstractmethod

class AbstractSet(ABC):

    @abstractmethod
    def add(self, element):
        pass

    @abstractmethod
    def remove(self, element):
        pass

    @abstractmethod
    def contains(self, element) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def union(self, other) -> 'AbstractSet':
        pass

    @abstractmethod
    def intersection(self, other) -> 'AbstractSet':
        pass

    @abstractmethod
    def elements(self):
        pass


class BuiltInSet(AbstractSet):

    def __init__(self):
        self.data = set()   # vestavěná Python množina

    def add(self, element):
        self.data.add(element)

    def remove(self, element):
        self.data.remove(element)

    def contains(self, element):
        return element in self.data

    def size(self):
        return len(self.data)

    def union(self, other):
        result = BuiltInSet()

        for x in self.data:
            result.add(x)

        for x in other:
            result.add(x)

        return result

    def intersection(self, other):
        result = BuiltInSet()

        for x in self.data:
            if other.contains(x):
                result.add(x)

        return result

    def elements(self):
        return self.data

    def __iter__(self):
        return iter(self.data)


if __name__ == "__main__":
    a = BuiltInSet()
    a.add(1)
    a.add(2)
    a.add(3)

    b = BuiltInSet()
    b.add(3)
    b.add(4)

    print(a.contains(2))
    print(a.size())

    c = a.union(b)
    print(list(c))

    d = a.intersection(b)
    print(list(d))