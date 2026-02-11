import mmh3

class set :
    def __init__(self,length):
        self.length = length
        self.list = []
        for i in range(length):
            self.list.append([])
        print(self.list)
        
    def add(self,input):
        if not isinstance(input,list):
            input = [input]
        for i in input:
            hash = (mmh3.hash(str(i))) % self.length
            if not i in self.list[hash]:
                self.list[hash].append(i)
        print(self.list)
    
    def delete(self,input):
        if not isinstance(input,list):
            input = [input]
            
        for i in input:
            hash = (mmh3.hash(str(i))) % self.length
            self.list[hash] = list(filter((i).__ne__, self.list[hash]))
        print(self.list)
    
    def search(self,input : int):
        hash = (mmh3.hash(str(input))) % self.length
        if input in self.list[hash]:
            print('item is present at' f'bucket: {hash} pos: {self.list[hash].index(input)} ')
            return True
        else:
            print('item not in set')
        
        
mainSet = set(10)

mainSet.add([1,3,1])

mainSet.delete(1)

mainSet.search(1)

mainSet.search(3)

