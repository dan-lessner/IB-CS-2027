setlist1 = []
frequency = {}

def add_set(item):
    if item not in frequency:
        frequency[item] = 0
    if item not in setlist1:
        frequency[item] += 1
    if item in setlist1:
        frequency[item] += 1    
    if item not in setlist1:
        setlist1.append(item)
    return setlist1

def remove_set(item):
    if item not in frequency:
        frequency[item] = 0

    if item not in setlist1:
        frequency[item] += 1
    if item in setlist1:
        frequency[item] += 1   
    if item in setlist1:
        setlist1.remove(item)
    return setlist1


def mysort(item):

    return frequency.get(item, 0)


add_set("apple")
add_set("banana")   
add_set("apple")  
add_set("optimus prime")  
remove_set("apple")
add_set("apple")
add_set("banana")  
setlist1.sort(key=mysort, reverse=True)

print(f"Set: {setlist1}")