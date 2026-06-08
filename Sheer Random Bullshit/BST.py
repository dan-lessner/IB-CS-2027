import math
class node:
    def __init__(self,value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self, arr):
        self.root = node(arr[len(arr)//2])
        self.tree = [self.root]
        for i in range(1,len(arr)):
            print("e: " + str(arr[i]))
            self.insert(self.root, arr[i])
    
    def insert(self, root, val):
        if root is None:
            print(f"Returned: {val}")
            return node(val)
        if root.value == val:
            print(f"Repeated: {val}")
            return root
        if root.value < val:
            print(f"Right: {val}")
            root.right = self.insert(root.right,val)
        elif root.value >val:
            print(f"Left: {val}")
            root.left = self.insert(root.left,val)
        return root
        
                
    
    def getChildIndexList(self,i):
        return [(2*(i+1) -1), 2*(i+1)]
    
    def getParentIndex(self,i):
        return math.floor((i+1)/2) -1
    
    def print (self,root):
        if root:
            self.print(root.left)
            print(f"Val: {root.value}")
            self.print(root.right)
            
            
        


tList = [17, 42, 89, 105, 238, 376, 491, 604, 752, 918, 1234, 2076, 3490, 4158, 5621, 6789, 7340, 8012, 9563, 64,68,89,1098]

penis = BST(tList)

penis.print(penis.root)
