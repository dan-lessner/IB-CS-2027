"""
Measuring the performance of binary search.

It tries to find each element in the given sorted list and counts the number 
of comparisons needed to find it. Finally, it calculates the average 
across all box sizes.

Is it correct? How do you make sure?
"""

items = [145, 687, 58, 68, 278, 149, 296, 382, 398, 426, 827, 654, 257, 12, 16, 8, 147, 1028, 283, 647, 2, 48, 12]
items = sorted(items)
print(sorted(items))

total = 0
for pokus in items :
    count = 0
    indexhigh = (len(items) - 1)
    indexlow = (0)  
    while indexhigh != indexlow: 
        count += 1
        index = (indexhigh + indexlow) / (2)
        hledam = items[int(index)]
        if hledam == pokus:
            break
        elif hledam > pokus:
            indexhigh = index
        else:
            indexlow = index
    total = total + count
print(len(items), total/len(items))
