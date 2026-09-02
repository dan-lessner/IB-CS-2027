import math
class quickSort ():
    def __init__(self,arr):
        self.arr = arr
        self.length = len(arr)
    
    def sort(self,array = None):
        if array is None:
            array = self.arr
        print("Unsorted: ", array)
        if len(array) <= 1:
            print("returning: ", array)
            return array
        else:
            print("Sorting: ", array)
            pivotIndex = len(array)//2
            print("Pivot: ", pivotIndex)
            pivot = array[pivotIndex]
            print("Pivot Value: ", pivot)
            left = []
            mid = []
            right = []
            for i in range(len(array)):
                if array[i] == pivot:
                    mid.append(array[i])
                elif array[i] < pivot:
                    left.append(array[i])
                elif array[i] > pivot:
                    right.append(array[i])
            return(self.sort(left) + mid + self.sort(right))

test_list = [47, 12, 89, 3, 56, 24, 91, 18, 72, 5, 63, 30, 77, 1, 44, 68, 20, 95, 38, 14, 52, 9,3,3,3]

h = quickSort(test_list)
print("sorted: ", h.sort())