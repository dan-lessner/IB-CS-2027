#  :3                 :3                 :3                 :3                 :3                 :3

def binary_search(elem, sorted_list):

    #checking whether the list is sorted
    for i in range(len(sorted_list)-1):         
        if sorted_list[i]>sorted_list[i+1]:
            return ValueError("list not sorted")

    list_len = len(sorted_list)

    #Cheching whether the number of elements in the list is even or odd, and choosing the pivot based on it
    if list_len%2 == 1:             
        index = (list_len-1)//2
        pivot = sorted_list[index]
    else:
        index = list_len//2
        pivot = sorted_list[index]
    
    #Comparing the pivot to the searched element, and continuing based on the result
    if elem == pivot:     
        return index
    if elem < pivot:
        return binary_search(elem, sorted_list[:index:])
    else:
        return (index + binary_search(elem, sorted_list[index::]))

list = [1, 2, 5, 6, 7, 12, 15, 16, 19, 26, 59, 63, 71]

print(binary_search(71, list))