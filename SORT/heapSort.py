
class heap():
    def __init__(self,arr):
        self.arr = arr
        self.length = len(arr)
    
    def print(self):
        print("Array: ",self.arr, " Length: ", self.length)


    def siftDown(self, cutoff = 0,index = 0):
            
            leftIndex = self.findChild(index)[0]
            rightIndex = self.findChild(index)[1]
            
            left = self.arr[leftIndex] if leftIndex < self.length - cutoff else float("-inf")
            right = self.arr[rightIndex] if rightIndex < self.length - cutoff else float("-inf")
            print("Array: ", self.arr,"Left: ", left, " Right: ", right,"SiftDown: ", self.arr[index], " Cutoff: ", cutoff, " Index: ", index)
            
            
            if self.arr[index] > left and self.arr[index] > right:
                return
            else:
                if left == right:
                    self.arr[index], self.arr[leftIndex] = self.arr[leftIndex], self.arr[index]
                    self.siftDown(cutoff, leftIndex)
                else:
                    if self.arr[index] < right and right != float("-inf"):
                        self.arr[index], self.arr[rightIndex] = self.arr[rightIndex], self.arr[index]
                        self.siftDown(cutoff, rightIndex)
                    elif self.arr[index] < left and left != float("-inf"):
                        self.arr[index], self.arr[leftIndex] = self.arr[leftIndex], self.arr[index]
                        self.siftDown(cutoff, leftIndex)     
    
    def findChild(self, index):
        pos = index*2 + 1
        return [pos, pos+1]
    
    def sort(self):
        cutoff = 0
        print("Unsorted: ", self.arr)
        for i in range(self.length-1,0,-1):
            print("FirstHeapIndex:",i)
            self.siftDown(0,i)
            
        for i in range(self.length):
            self.siftDown(cutoff,0)
            cutoff += 1    
            self.arr[0], self.arr[-cutoff] = self.arr[-cutoff], self.arr[0] 
        print("Sorted: ",self.arr)  
        return self.arr  
        
    def findParent(self, index):
        pos = int((float(index-1)/2))
        return pos

test_list = [1,2,3,4,5,6,7,8,9]

h = heap(test_list)
h.sort()
h.print()