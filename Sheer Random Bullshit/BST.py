import math
class node:
    def __init__(self,value):
        self.value = value
        self.left = None
        self.right = None
#class for a node, does nothing on its own

class BST:
    def __init__(self, arr):
        self.root = node(arr[len(arr)//2])
        self.tree = [self.root]
        for i in range(1,len(arr)):
            print("e: " + str(arr[i]))
            self.insert(self.root, arr[i])
    #inits the class (cuz ofc) and finds the most optimal root
    
    def insert(self, root, val): #This function inserts an element into the BST without balancing (idk how to do red black lol), it checks for duplicates aswell 
        if root is None:
            print(f"Returned: {val}")
            return node(val)
        #if node with specified value doesnt exist create node with the value
        if root.value == val:
            print(f"Repeated: {val}")
            return root
        #if value alr exists, exit and skip
        if root.value < val:
            print(f"Right: {val}")
            root.right = self.insert(root.right,val)
        #if value is larger than root then set right node as new root (even if it does not exist)
        elif root.value >val:
            print(f"Left: {val}")
            root.left = self.insert(root.left,val)
        #if value is smaller than root then set left node as new root (even if it does not exist)
        return root
        
    def print (self,root):
        if root:
            self.print(root.left)
            print(f"Val: {root.value}")
            self.print(root.right)
        #if the root exists then run recursively for the left child, then print the value, then run it recursively for the right child (these children do not need to exist due to the if statement at the start)
            
            
        


tList = [17, 42, 89, 105, 238, 376, 491, 604, 752, 918, 1234, 2076, 3490, 4158, 5621, 6789, 7340, 8012, 9563, 64,68,89,1098]

penis = BST(tList)

penis.print(penis.root)
