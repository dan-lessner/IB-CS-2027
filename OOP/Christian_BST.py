
nodeList =[]
inputList = [50, 30, 70, 20, 40, 60, 80, 10, 35, 65]
idCount = 1
class node :
    def __init__ (self,value,sChild,bChild,id):
            self.value = value
            self.sChild = sChild
            self.bChild = bChild
            self.id = id
    def penis(self, cNode, inputValue):
        global idCount
        if inputValue > cNode.value:
            if cNode.bChild == 0:
                cNode.bChild = idCount
                nodeList.append(node(inputValue,0,0,idCount))
                idCount += 1
            else:
                for i in nodeList:
                    if i.id == cNode.bChild:
                        self.penis(i,inputValue)
        if inputValue < self.value:
            if cNode.sChild == 0:
                cNode.sChild = idCount
                nodeList.append(node(inputValue,0,0,idCount))
                idCount += 1
            else:
                for i in nodeList:
                    if i.id == cNode.sChild:
                        self.penis(i,inputValue)
    
    
                
def generate(current,inputValue):
    global idCount
    if inputValue > current.value:
        if current.bChild == 0:
            current.bChild = idCount
            nodeList.append(node(inputValue,0,0,idCount))
            idCount += 1
        else:
            for i in nodeList:
                if i.id == current.bChild:
                    generate(i,inputValue)
    if inputValue < current.value:
        if current.sChild == 0:
            current.sChild = idCount
            nodeList.append(node(inputValue,0,0,idCount))
            idCount += 1
        else:
            for i in nodeList:
                if i.id == current.sChild:
                    generate(i,inputValue)
    
nodeList.append(node(inputList.pop(0),0,0,0))
#for i in inputList:
    #nodeList[0].penis(nodeList[0],i)

#for i in inputList:
    #generate(nodeList[0],i)
for i in nodeList:
    
    print(i.value,i.sChild,i.bChild,i.id)
                            
