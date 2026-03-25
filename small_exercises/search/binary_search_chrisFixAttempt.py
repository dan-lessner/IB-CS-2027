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
    indexhigh = (len(items) - 1)
    indexlow = (0)  
    while indexhigh != indexlow: 
        #print("new iteration")
        #print("element: ", x)
        #print("low: ", indexlow)
        #print("high: ", indexhigh)
        #print( items[indexlow:indexhigh+1])
        count += 1
        pivot = (indexhigh + indexlow) // (2) 
       # print("pivot", pivot)
        midElement = items[pivot]
        if midElement == x:
            #print("Break!")
            break
        elif midElement > x:
            #print("Smaller")
            indexhigh = pivot -1
        elif midElement < x:
            #print("Bigger")
            indexlow = pivot + 1
        else:
            print("Catastrophic Failure... How did you do this?")
    print("IterCount: ", count)
    total += count
print(len(items), total/len(items))