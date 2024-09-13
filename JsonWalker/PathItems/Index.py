from .PathItem import PathItem
from .Constants import INDEX_START, INDEX_END, INDEX_RANGE, INDEX_WILDCARD
from typing import Any

"""Index is a PathItem that represents an index in a list"""
class Index(PathItem):
    def __init__(self, indexStr: str) -> None:
        """Create a new Index object.

        Args:
            indexStr (str): a string of the index or range
        """
        index = self._stripIndex(indexStr)
        if INDEX_RANGE in index:
            start, end = index.split(INDEX_RANGE)

            self._properIndexSyntax(start)
            self._properIndexSyntax(end)

            self.start = self._convertToIndex(start)
            self.end = self._convertToIndex(end)

            self.context = 'range'
        else:
            self._properIndexSyntax(index)

            self.start = self._convertToIndex(index)
            self.end = -1
            
            self.context = 'index'

    def _stripIndex(self, index: str) -> str:
        """Strip the index string of the index delimiters.

        Args:
            index (str): the index string to strip

        Returns:
            str: the stripped index string
        """
        assert index.startswith(INDEX_START) and index.endswith(INDEX_END), f"Index must be in the form {INDEX_START}n{INDEX_END}"
        return index[1:-1]

    def _properIndexSyntax(self, check: str) -> None:
        """Check if the index is a valid integer or wildcard.

        Args:
            check (str): the index string to check
        """
        assert check.replace("-", "").isdigit() or check == INDEX_WILDCARD, f"Index must be an integer or {INDEX_WILDCARD}"

    def _convertToIndex(self, index: str) -> int | None:
        """Convert the index string to an integer.

        Args:
            index (str): the index string to convert

        Returns:
            int | None: the converted index or None if it is a wildcard
        """
        if index == INDEX_WILDCARD:
            return None
        return int(index)

    def apply(self, current: str, context: list) -> tuple:
        """Apply the Index to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the updated value and context list
        """
        assert self.context in ['index', 'range'], "Invalid context"

        if not isinstance(current, list):
            return current, context

        if self.context == 'index':
            return self._handleIndex(current), context
        else:
            return self._handleRange(current), context
    
    def _handleIndex(self, current: list) -> Any:
        """Handles the index access of the list.

        Args:
            current (list): the current list

        Returns:
            Any: the value at the index
        """
        if self.start is None:
            return current
        
        self.start = self._handleNegativeIndex(current, self.start)
        if self._notInRange(self.start, current):
            return None
        
        return current[self.start]
    
    def _handleRange(self, current: list) -> list:
        """Handles the range access of the list.

        Args:
            current (list): the current list

        Returns:
            list: the values in the range
        """
        if self.start is None:
            self.start = 0
        if self.end is None:
            self.end = len(current)

        self.start = self._handleNegativeIndex(current, self.start)
        self.end = self._handleNegativeIndex(current, self.end)
        
        return current[self.start:self.end]
    
    def _notInRange(self, index: int, current: list) -> bool:
        """Check if the index is out of range.

        Args:
            index (int): the index to check
            current (list): the current list

        Returns:
            bool: True if the index is out of range, False otherwise
        """
        return index >= len(current) or index < 0
    
    def _handleNegativeIndex(self, current: list, index: int) -> int:
        """Handle negative indexes by converting them to positive indexes.

        Args:
            current (list): the current list
            index (int): the index to handle

        Returns:
            int: the updated index
        """
        if index < 0:
            return len(current) + index
        return index