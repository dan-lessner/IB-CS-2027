#  :3                 :3                 :3                 :3                 :3                 :3

def binary_search(arr, elem):
    # sorted = True

    #checking whether the list is sorted
    # for i in range(len(arr)-1):         
    #     if arr[i]>arr[i+1]:
    #         sorted = False
        
    # if not sorted:
    #     arr = quick_sort(arr)
    #     print(arr)

    return _binary_search(arr, elem)


def _binary_search(sorted_list, elem):

    #Cheching whether the number of elements in the list is even or odd, and choosing the pivot based on it
    list_len = len(sorted_list)

    if list_len == 1:
        if sorted_list[0] != elem:
            return -1
        else:
            return 0

    if list_len%2 == 1:             
        index = (list_len-1)//2
    else:
        index = list_len//2
    
    pivot = sorted_list[index]
    
    #Comparing the pivot to the searched element, and continuing based on the result
    if elem == pivot:     
        return index
    elif elem < pivot:
        fin_ind = _binary_search(sorted_list[:index], elem)
        if fin_ind == -1:
            return -1
    else:
        fin_ind = _binary_search(sorted_list[index:], elem)
        if fin_ind == -1:
            return -1
        fin_ind = index + fin_ind

    return fin_ind

def quick_sort(arr):
    arr_len = len(arr)

    if arr_len == 1:
        return arr

    if arr_len == 0:
        return []
    
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