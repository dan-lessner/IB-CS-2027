import random
import importlib

filename = input("Enter the filename of the module to test: ")

try:
    imported_module = importlib.import_module(filename)
    binary_search = imported_module.binary_search
except (ImportError, AttributeError) as e:
    print(f"Error importing binary_search from {filename}: {e}")
    exit(1)

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Test cases
print("=== Running Tests ===")

# Test 1: Search for first element
arr = sorted(random.sample(range(101), 20))
try:
    assert binary_search(arr, arr[0]) == 0, f"Expected index 0, got {binary_search(arr, arr[0])}"
    print(f"Test 1 {GREEN}passed{RESET}: Search for first element")
except AssertionError as e:
    print(f"Test 1 {RED}failed{RESET} for {arr}: {e}")

# Test 2: Search for last element
arr = sorted(random.sample(range(101), 20))
i = len(arr) - 1
try:
    assert binary_search(arr, arr[-1]) == i, f"Expected index {i}, got {binary_search(arr, arr[-1])}"
    print(f"Test 2 {GREEN}passed{RESET}: Search for last element")
except AssertionError as e:
    print(f"Test 2 {RED}failed{RESET} for {arr}: {e}")

# Test 3: Search for middle element
arr = sorted(random.sample(range(101), 20))
i = len(arr) // 2
try:
    assert binary_search(arr, arr[i]) == i, f"Expected index {i}, got {binary_search(arr, arr[i])}"
    print(f"Test 3 {GREEN}passed{RESET}: Search for middle element")
except AssertionError as e:
    print(f"Test 3 {RED}failed{RESET} for {arr}: {e}")

# Test 4: Search for arbitrary element
arr = sorted(random.sample(range(101), 20))
i = random.randint(0, len(arr) - 1)
try:
    assert binary_search(arr, arr[i]) == i, f"Expected index {i}, got {binary_search(arr, arr[i])}"
    print(f"Test 4 {GREEN}passed{RESET}: Search for arbitrary element")
except AssertionError as e:
    print(f"Test 4 {RED}failed{RESET} for {arr}: {e}")

# Test 5: Search for random element in large list
arr = sorted(random.sample(range(10000), 1000))
i = random.randint(0, len(arr) - 1)
try:
    assert binary_search(arr, arr[i]) == i, f"Expected index {i}, got {binary_search(arr, arr[i])}"
    print(f"Test 5 {GREEN}passed{RESET}: Search for random element in large list")
except AssertionError as e:
    print(f"Test 5 {RED}failed{RESET} for large list: {e}")

# Test 6: Element not found
arr = [1, 2, 3, 4, 5, 6, 7, 8]
try:
    assert binary_search(arr, 99) == -1, f"Expected index -1, got {binary_search(arr, 99)}"
    print(f"Test 6 {GREEN}passed{RESET}: Element not found")
except AssertionError as e:
    print(f"Test 6 {RED}failed{RESET} for {arr}: {e}")

# Test 7: Unsorted list
arr = [5, 2, 8, 1, 9, 3, 7]
try:
    assert binary_search(arr, 7) == 6, f"Expected index 6, got {binary_search(arr, 7)}"
    print(f"Test 7 {GREEN}passed{RESET}: Search for element in unsorted list")
except AssertionError as e:
    print(f"Test 7 {RED}failed{RESET} for {arr}: {e}")