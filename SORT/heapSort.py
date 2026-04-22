
class heap():
    def __init__(self,arr):
        self.arr = arr
        self.length = len(arr)
        self.cutoff = 0

    def heapify(self):
        for i in range(self.length-(self.cutoff+1),0,-1):
            pIndex = self.findParent(i)
            #print(self.arr[i],self.arr[pIndex])
            if self.arr[i] > self.arr[pIndex]:
                self.arr[i], self.arr[pIndex] = self.arr[pIndex], self.arr[i]
                #print("Switch!!: ",self.arr[i], self.arr[pIndex])
        #print(self.arr)
    
    def sort(self):
        print("Unsorted: ", self.arr)
        for _ in range(self.length):
            self.heapify()
            self.cutoff += 1    
            self.arr[0], self.arr[-self.cutoff] = self.arr[-self.cutoff], self.arr[0] 
        print("Sorted: ",self.arr)  
        return self.arr  
        
    def findParent(self, index):
        pos = int((float(index-1)/2))
        return pos

test_list = [47, 12, 89, 3, 56, 24, 91, 18, 72, 5, 63, 30, 77, 1, 44, 68, 20, 95, 38, 14, 52, 9]

h = heap(test_list)
h.sort()