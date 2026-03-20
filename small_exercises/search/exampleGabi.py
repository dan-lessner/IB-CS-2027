def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    while left <= right:
        mid = (left + right) // 2  #middle index

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1  #right half
        else:
            right = mid - 1  #left half

    return target