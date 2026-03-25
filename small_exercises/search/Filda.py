def binary_search(arr, target):
    dole = 0
    nahoře = len(arr) - 1
    arr.sort()
    while dole <= nahoře:
        mid = (dole + nahoře) // 2
        guess = arr[mid]
        if guess == target:
            return mid
        if guess > target:
            nahoře = mid - 1
        else:
            dole = mid + 1
    return -1
# Test cases
print("=== Binary Search Test Cases ===\n")

# Test 1: Search for first element
arr1 = [1, 3, 5, 7, 9, 11, 13, 15]
print(f"Array: {arr1}")
print(f"Search for 1: {binary_search(arr1, 1)} (expected: 0)")
print()

# Test 2: Search for last element
arr2 = [2, 4, 6, 8, 10, 12, 14, 16, 18]
print(f"Array: {arr2}")
print(f"Search for 18: {binary_search(arr2, 18)} (expected: 8)")
print()

# Test 3: Search for middle element
arr3 = [10, 20, 30, 40, 50, 60, 70]
print(f"Array: {arr3}")
print(f"Search for 40: {binary_search(arr3, 40)} (expected: 3)")
print()

# Test 4: Search for arbitrary element
arr4 = [5, 15, 25, 35, 45, 55, 65, 75]
print(f"Array: {arr4}")
print(f"Search for 35: {binary_search(arr4, 35)} (expected: 3)")
print()

# Test 5: Element not found
arr5 = [1, 2, 3, 4, 5, 6, 7, 8]
print(f"Array: {arr5}")
print(f"Search for 99: {binary_search(arr5, 99)} (expected: -1)")
print()

# Test 6: Unsorted list
arr6 = [5, 2, 8, 1, 9, 3, 7]
print(f"Array: {arr6}")
print(f"Search for 7: {binary_search(arr6, 7)} (correct is 4, but who knows what happens)")
    

