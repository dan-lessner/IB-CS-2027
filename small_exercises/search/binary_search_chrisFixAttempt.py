"""
Measuring the performance of binary search.

It tries to find each element in the given sorted list and counts the number 
of comparisons needed to find it. Finally, it calculates the average 
across all box sizes.

Is it correct? How do you make sure?
"""

items = [145, 687, 58, 68, 278, 149, 296, 382, 398, 426, 827, 654, 257, 12, 16, 8, 147, 1028, 283, 647, 2, 48, 12]
items = sorted(items)

total = 0
for x in items :
    print("\n-----------------------------------\n")
    print("element: " , x)
    count = 0
    indexHigh = (len(items) - 1)
    indexLow = (0)  
    while indexHigh != indexLow: 
        #print("new iteration")
        #print("element: ", x)
        #print("low: ", indexLow)
        #print("high: ", indexHigh)
        #print( items[indexLow:indexHigh+1])
        count += 1
        pivot = (indexHigh + indexLow) // (2) 
       # #print("pivot", pivot)
        midElement = items[pivot]
        if midElement == x:
            #print("Break!")
            break
        elif midElement > x:
            #print("Smaller")
            indexHigh = pivot -1
        elif midElement < x:
            #print("Bigger")
            indexLow = pivot + 1
        else:
            print("Catastrophic Failure... How did you do this?")
    print("IterCount: ", count)
    total += count
print("Average time: ",total/len(items))