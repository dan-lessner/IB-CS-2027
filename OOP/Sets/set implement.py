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
            return False
            print('item not in set')
    def setPrint (self):
        returnList = []
        for i in self.list:  
            returnList.extend(i)
        print(returnList)
        return returnList
    
    def clear(self):
        self.list = []
        for i in range(self.length):
            self.list.append([])
    
    def combine(self,externalSet : object, returnLength : int):
        tempList = []
        returnList = []
        tempList.extend(self.setPrint())
        print('self: ' + str(self.setPrint()))
        tempList.extend(externalSet.setPrint())
        print('external: ' + str(externalSet.setPrint()))
        
        print('templist' + str(tempList))
        for i in tempList:
            if i not in returnList:
                returnList.append(i)
        print(returnList)
        returnSet = set(returnLength)
        returnSet.add(returnList)
        return returnSet
    
    
    #DIFF NEFUNGUJE
    def difference(self,externalSet : object, returnLength : int):
        seenList = []
        tempList = []
        popList = []

        tempList.extend(self.setPrint())
        print('self: ' + str(self.setPrint()))
        tempList.extend(externalSet.setPrint())
        print('external: ' + str(externalSet.setPrint()))
        
        for i in range(len(tempList)):
            if tempList[i] not in seenList:
                seenList.append(tempList[i])
            elif tempList[i]  in seenList:
                popList.append(tempList[i])

        for i in popList:
            while True:
                if i in tempList:
                    tempList.remove(i)
                else:
                    break
        
        print('diffset: ' + str(tempList))
        returnSet = set(returnLength)
        returnSet.add(tempList)
        return returnSet
        

                        
                
        
        
        
mainSet = set(20)
subSet = set(10)

subSet.add([1,3,7,2,4,6,5])
mainSet.add([1,3,1,2,4,6,1])

mainSet.difference(subSet)
