from AbstractSet import AbstractSet
import math

#name: Christian
#Class: 67F
#Age: 67 years old
#Project: Hash Set But Stupider than Jenda's
#Short explanation: Uses hashing to get element bucket indexes instead of just searching thru a list, meaning that we always should have a O(1)
#Long explanation: https://www.youtube.com/watch?v=xvFZjo5PgG0

class set (AbstractSet):
    def __init__(self,length):
        self.length = length
        self.list = [[] for _ in range(self.length)]
        self.population = 0
    
    def getIndex(self, element):
        returnVar = 1
        for x in list(str(element)):
            returnVar *= ord(x)
        return (returnVar % self.length)
    
    
    def resize(self, newCap):
        old = self.list
        self.length = math.ceil(newCap)
        self.list = [[] for _ in range(self.length)]
        self.population = 0
        for x in old:
            self.add(x)
        
    def add(self,input):
        if not isinstance(input,list):
            input = [input]
        for x in input:
            hash = self.getIndex(x)
            if x not in self.list[hash]:
                self.population += 1
                self.list[hash].append(x)
        if self.population > self.length:
            self.resize(self.length * 1.2)
    
    def remove(self,input):
        if not isinstance(input,list):
            input = [input]
            
        for i in input:
            hash = self.getIndex(i)
            self.list[hash] = list(filter((i).__ne__, self.list[hash]))
    
    def contains(self,input : int):
        hash = self.getIndex(input)
        if input in self.list[hash]:
            print('item is present at' f'bucket: {hash} pos: {self.list[hash].index(input)} ')
            return True
        else:
            print('item not in set')
            return False      
    
    def size (self):
        return (self.length)
    
    def elements(self):
        returnList = []
        for i in self.list:  
            returnList.extend(i)
        return returnList
    
    def clear(self):
        self.list = []
        for i in range(self.length):
            self.list.append([])
    
    def union(self,externalSet : object):
        returnSet = set(self.length)
        returnSet.add(self.setStock() + externalSet.setStock())
        return returnSet
    
    def setPrint(self):
        print(self.list)
    
    def difference(self,externalSet : object):
        returnSet = set(self.length)
        for i in self.setStock():
            if externalSet.search(i) == False:
                returnSet.add(i)
        return returnSet
    
    def intersection(self,externalSet : object):
        returnSet = set(self.length)
        for i in self.setStock():
            if externalSet.search(i) == True:
                returnSet.add(i)
        return returnSet
    
    def isSubset(self, externalSet : object):
        if self.setStock() in externalSet.setStock():
            return True
        else:
            return False
    
    def __iter__(self):
        return iter(self.list)
        

                        
# Add ur code here ig:

mainSet = set(5)
mainSet.add([1,4,6,3,7,9,5,4,5,7,5,4])

mainSet.setPrint()

print(mainSet.elements())