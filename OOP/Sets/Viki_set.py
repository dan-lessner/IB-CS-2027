from AbstractSet import AbstractSet
class MySet(AbstractSet):

    def __init__(self):
        self.data = []      # creates a list of items, stores it as pairs
        self.set_size = 0   # counts only active items

    def add(self, element):
        # looks for the element
        for pair in self.data:
            if pair[0] == element: 
                if pair[1] == 0:
                    # if inacctive, then change its value, activate it
                    pair[1] = 1
                    self.set_size += 1
                return  # already active, ignore it
        # it is a new item, add it as the pair to the end
        self.data.append([element, 1])
        self.set_size += 1

    def remove(self, element):
        for pair in self.data:
            if pair[0] == element:
                if pair[1] == 1:
                    # if it is active, then just make it inactive, change it to 0
                    pair[1] = 0
                    self.set_size -= 1
                    return
        raise ValueError("Not found") #this happens, if the value doesnt exist

    def contains(self, element) -> bool: # is it in the set
        for pair in self.data:
            if pair[0] == element and pair[1] == 1:
                return True
        return False
    #bool = this function will always return boolean, True or False


    def size(self) -> int:
        return self.set_size


    def union(self, other) -> 'AbstractSet':
        # everything in a combo, no duplicates
        result = MySet()  
        for pair in self.data:
            if pair[1] == 1:        # only active items
                result.add(pair[0])
        for item in other.elements():
            result.add(item)        
        return result

    def intersection(self, other) -> 'AbstractSet':
        # both sets have it
        result = MySet()
        for pair in self.data:
            if pair[1] == 1:                # active items only
                if other.contains(pair[0]): # controls, if the item exists in both sets
                    result.add(pair[0])
        return result

    def elements(self):
        # gives out the items, one by one, it doesnt close the loop
        for pair in self.data:
            if pair[1] == 1:
                yield pair[0]


if __name__ == "__main__":
    a = MySet() 
    a.add("red")
    a.add("purple")
    a.add("red")   
    a.add("blue")

    print("Set A:", list(a.elements()))      
    print("Is there red:", a.contains("red"))  
    print("Size:", a.size())                  

    a.remove("red")
    print("After remove:", list(a.elements())) 
    print("Size:", a.size())      

    a.add("red")  
    print("After add:", list(a.elements()))

    b = MySet()
    b.add("purple")
    b.add("pink")

    c = a.union(b)
    print("Union:", list(c.elements()))       

    d = a.intersection(b)
    print("Intersection:", list(d.elements())) 