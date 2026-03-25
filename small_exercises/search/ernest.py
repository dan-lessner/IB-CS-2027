def binary_search(arr, target):
    if len(arr) == 1:
        if arr[0] == target:
            return 0
        else:
            return -1
    split = len(arr)//2
    idx = 0
    if arr[split] == target:
        return split
    elif target <= arr[split]:
        idx = binary_search(arr[:split], target)
        if idx == -1:
            return -1
    else:
        idx = binary_search(arr[split:], target)
        if idx == -1:
            return -1
        idx = split + idx
    return idx
