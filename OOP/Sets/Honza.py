from AbstractSet import AbstractSet

# the set is essentially a list of 0 and 1 - when certain number N is in the set, the Nth position is 1 (indexed from 0)
class Set(AbstractSet):
    def __init__(self):
        self.data = [0]     # the list of 0s and 1s
        self.max = 0        # largest number in the set (amount of 0s and 1s in the list)
        self.set_size = 0   # amount of numbers in the set

    def add(self, element):
        if self.max < element:    # adding 0s in case the number added is larger than the amount of 0s and 1s in the list (increasing the range of the list)
            for i in range(element-self.max):
                self.data.append(0)
            self.max = element
        self.data[element] = 1
        self.set_size += 1

    def remove(self, element):
        if self.max < element:   #showing error in case the number that is supposed to be removed is larger than the list of 0s and 1s
            raise ValueError("Value is not in the set")
        else:
            self.data[element] = 0

    def contains(self, element):
        if self.max < element:
            return False
        elif self.data[element] == 0:
            return False
        return True

    def size(self):
        return self.set_size
    
    def union(self, other):
        union_set = Set()
        check_size = 0
        if self.max < other.max:
            check_size = self.max+1
        else:
            check_size = other.max+1

        for i in range(check_size):
            if self.data[i] == 1:
                union_set.add(i)
            elif other.data[i] == 1:
                union_set.add(i)
        
        return union_set.data
    
    def intersection(self, other):
        inter_set = Set()
        if self.max < other.max:
            for i in range(self.max+1):
                if self.data[i] == 1:
                    if other.data[i] == 1:
                        inter_set.add(i) 
        else:
            for i in range(other.max+1):
                if other.data[i] == 1:
                    if self.data[i] == 1:
                        inter_set.add(i)
        
        return inter_set.data
    
    def elements(self):
        for i in range(len(self.data)):
            if self.data[i] == 1:
                yield i

    def __iter__(self):
        return