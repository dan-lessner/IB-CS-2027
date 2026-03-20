#  :3                 :3                 :3                 :3                 :3                 :3

def binary_search(arr, elem):
    sorted = True

    #checking whether the list is sorted
    for i in range(len(arr)-1):         
        if arr[i]>arr[i+1]:
            sorted = False
        
    if not sorted:
        sorted_arr = quick_sort(arr)

    return _binary_search(sorted_arr, elem)


def _binary_search(sorted_list, elem):

    #Cheching whether the number of elements in the list is even or odd, and choosing the pivot based on it
    list_len = len(sorted_list)

    if list_len%2 == 1:             
        index = (list_len-1)//2
    else:
        index = list_len//2
    
    pivot = sorted_list[index]
    
    #Comparing the pivot to the searched element, and continuing based on the result
    if elem == pivot:     
        return index
    if elem < pivot:
        return _binary_search(sorted_list[:index], elem)
    if list_len == 1:
        return -1
    if _binary_search(sorted_list[index:], elem) == -1:
        return -1
    return (index + _binary_search(sorted_list[index:], elem))

def quick_sort(arr):
    arr_len = len(arr)

    if arr_len == 1:
        return arr

    pivot = arr[0]

    left_side = []
    right_side = []

    for i in range(arr_len):
        if i == 0:
            continue
        if arr[i] <= pivot:
            left_side.append(arr[i])
        if arr[i] > pivot:
            right_side.append(arr[i])

    return quick_sort(left_side) + [pivot] + quick_sort(right_side)