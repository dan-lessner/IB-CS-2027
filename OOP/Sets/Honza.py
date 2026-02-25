from AbstractSet import AbstractSet


class Set(AbstractSet):
    def __init__(self):
        self.data = [0]
        self.max = 0
        self.set_size = 0

    def add(self, element):
        if self.max < element:
            for i in range(element-self.size):
                self.data.append(0)
            self.max = element
        self.data[element] = 1
        self.set_size += 1

    def remove(self, element):
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