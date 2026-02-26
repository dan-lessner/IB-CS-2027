from AbstractSet import AbstractSet

class MrTeacherStoopidListSet(AbstractSet):
    """The stoopidest set implementation, using an unsorted list."""
    
    def __init__(self, elements=None):
        """Initialize the set with optional items."""
        self._elements = []
        if elements:
            for element in elements:
                self.add(element)
    
    def add(self, element):
        """Add an item to the set if not already present."""
        if element not in self._elements:
            self._elements.append(element)
    
    def remove(self, element):
        """Remove an item from the set. Raises KeyError if not found."""
        if element in self._elements:
            self._elements.remove(element)
        else:
            raise KeyError(element)
    
    def contains(self, element):
        """Check if element is in the set."""
        return element in self._elements

    def size(self):
        """Return the number of items in the set."""
        return len(self._elements)
    
    def union(self, other):
        """Return a new set with items from both sets."""
        result = MrTeacherStoopidListSet(self._elements)
        for item in other:
            result.add(item)
        return result
    
    def intersection(self, other):
        """Return a new set with items common to both sets."""
        result = MrTeacherStoopidListSet()
        for element in self._elements:
            for other_element in other:
                if element == other_element:
                    result.add(element)
        return result
    
    def elements(self):
        """Iterate over items in the set."""
        return self._elements