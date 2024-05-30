from .PathItem import PathItem
from .constants import INDEX_START, INDEX_END, INDEX_RANGE, INDEX_WILDCARD

"""Index is a PathItem that represents an index in a list"""
class Index(PathItem):
    def __init__(self, indexStr: str) -> None:
        """Create a new Index object.

        Args:
            indexStr (str): a string of the index or range
        """
        assert indexStr.startswith(INDEX_START) and indexStr.endswith(INDEX_END), f"Index must be in the form {INDEX_START}n{INDEX_END}"
        index = indexStr[1:-1]
        if INDEX_RANGE in index:
            start, end = index.split(INDEX_RANGE)
            assert start.replace("-", "").isdigit() or start == INDEX_WILDCARD, f"Start index must be an integer or {INDEX_WILDCARD}"
            self.start = int(start) if start != INDEX_WILDCARD else None

            assert end.replace("-", "").isdigit() or end == INDEX_WILDCARD, f"End index must be an integer or {INDEX_WILDCARD}"
            self.end = int(end) if end != INDEX_WILDCARD else None
            self.context = 'range'
        else:
            assert index.replace("-", "").isdigit() or index == INDEX_WILDCARD, f"Index must be an integer or {INDEX_WILDCARD}"
            self.start = int(index) if index != INDEX_WILDCARD else None
            self.end = -1
            self.context = 'index'

    def apply(self, current: str, context: list) -> tuple:
        """Apply the Index to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the updated value and context list
        """
        assert self.context in ['index', 'range'], "Invalid context"
        if isinstance(current, list):
            if self.context == 'index':
                if self.start is not None:
                    if self.start < 0:
                        return current[len(current) + self.start], context
                    return current[self.start], context
                return current, context
            elif self.context == 'range':
                if self.start is None:
                    self.start = 0
                if self.end is None:
                    self.end = len(current)
                if self.start < 0:
                    self.start = len(current) + self.start
                if self.end < 0:
                    self.end = len(current) + self.end
                return current[self.start:self.end], context
        return current, context