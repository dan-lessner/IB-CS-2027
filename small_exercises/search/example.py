def binary_search(arr, target):
    """
    Search for target in a sorted list.
    
    Args:
        arr: Sorted list of numbers
        target: Number to search for
        
    Returns:
        Index of target if found, -1 otherwise
    """
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1