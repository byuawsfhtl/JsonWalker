import itertools
from typing import Generator, Any, Optional

class JsonPath:
    """Base class for building chainable JSON path queries. Allows fluent querying of nested dictionaries and lists."""
    
    def __init__(self, prevPath: Optional['JsonPath'] = None) -> None:
        """Initialize a new JsonPath object.

        Args:
            prevPath (Optional[JsonPath]): the preceding path element in the chain
        """
        self.prevPath = prevPath
        self.contexts: list[Any] = []

    def _getFullPath(self) -> list['JsonPath']:
        """Build the complete path by following the chain backwards.

        Returns:
            list[JsonPath]: the full query chain of JsonPath nodes
        """
        path = []
        current = self
        while current:
            path.insert(0, current)
            current = current.prevPath
        return path

    def walk(self, data: dict|list) -> Generator[Any, None, None]:
        """Execute the path query on the given JSON-like data.

        Args:
            data (dict | list): the JSON-styled data structure to walk

        Yields:
            Any: aach matched element in the path
        """
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _traverse(self, current: Any, remainingPath: list['JsonPath'], contexts: list[Any]) -> Generator[Any, None, None]:
        """Recursively traverse the data structure according to the path.

        Args:
            current (Any): the current data element being examined
            remainingPath (list[JsonPath]): remaining path elements to apply
            contexts (list[Any]): accumulated context values

        Yields:
            Any: final results after full traversal
        """
        if current is None:
            return

        if not remainingPath:
            yield contexts + [current] if contexts else current
            return

        pathItem = remainingPath[0]
        yield from pathItem._apply(current, remainingPath[1:], contexts.copy())

    def _apply(self, current: Any, remainingPath: list['JsonPath'], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply this path item to the current data and continue traversal.

        Args:
            current (Any): current node in the JSON structure
            remainingPath (list[JsonPath]): path nodes left to apply
            contexts (list[Any]): context accumulated so far

        Yields:
            Any: traversal result
        """
        yield from self._traverse(current, remainingPath, contexts)

    def key(self, keyName: str, default: Any = None) -> "Key":
        """Creates a path segment that accesses a dictionary by a specific key.

        Args:
            keyName (str): the key to access in the dictionary
            default (Any, optional): a fallback value to use if the key is not found; defaults to None

        Returns:
            Key: a `JsonPath` segment that retrieves the value associated with `keyName`
        """
        return Key(keyName, default, self)

    def listIndex(self, idx: int) -> "Index":
        """Creates a path segment that accesses a specific index in a list.

        Args:
            idx (int): the index to access in the list. Negative indices are supported

        Returns:
            Index: a `JsonPath` segment that retrieves the item at the specified index
        """
        return Index(idx, self)

    def listSlice(self, start: Optional[int] = None, end: Optional[int] = None) -> "Slice":
        """Creates a path segment that accesses a range of elements in a list.

        Args:
            start (Optional[int], optional): the starting index of the slice (inclusive). Defaults to None (start of list)
            end (Optional[int], optional): the ending index of the slice (exclusive). Defaults to None (end of list)

        Returns:
            Slice: a `JsonPath` segment that yields elements within the given slice range
        """
        return Slice(start, end, self)

    def listAll(self) -> "Slice":
        """Creates a path segment that accesses all elements in a list.

        Returns:
            Slice: a `JsonPath` segment that iterates over all items in a list
        """
        return Slice(None, None, self)

    def keyContextAndValue(self) -> "KeyContextAndValue":
        """Creates a path segment that iterates through all key-value pairs in a dictionary.
        The keys are appended to the context, and the values are passed on to the next segment.

        Returns:
            DictItems: a `JsonPath` segment for dictionary iteration
        """
        return KeyContextAndValue(self)

    def addContext(self) -> "AddedContext":
        """Creates a path segment that adds the current value to the context.
        Useful for collecting intermediate values during path evaluation.

        Returns:
            AdditionalContext: a `JsonPath` segment that augments the context with the current value
        """
        return AddedContext(self)

    def multi(self, *paths: 'JsonPath') -> "MultiValue":
        """Creates a path segment that collects multiple values from different sub-paths

        Args:
            *paths (JsonPath): one or more sub-paths to evaluate from the current point

        Returns:
            MultiValue: a `JsonPath` segment that gathers values from each of the provided paths
        """
        return MultiValue(paths, self)


class Key(JsonPath):
    """Path element that accesses a dictionary key."""

    def __init__(self, key: str, default: Any = None, prevPath: Optional[JsonPath] = None) -> None:
        """Initiates the key path.

        Args:
            key (str): the dictionary key to access
            default (Any, optional): a fallback value if the key is not found; defaults to None
            prevPath (Optional[JsonPath]): the preceding path segment; defaults to None
        """
        super().__init__(prevPath)
        self.dictKey = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Applies the key lookup on a dictionary.
        If the current object is a dictionary, retrieve the value for the specified key.
        If not, skip key lookup and pass through the object unchanged.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing the matched value
        """
        if isinstance(current, dict):
            value = current.get(self.dictKey, self.default)
            yield from self._traverse(value, remainingPath, contexts)
        else:
            yield from self._traverse(current, remainingPath, contexts)


class Index(JsonPath):
    """Path element that accesses a list by index."""

    def __init__(self, index: int, prevPath: Optional[JsonPath] = None) -> None:
        """Initiates the index path.

        Args:
            index (int): the list index to access (supports negative indices)
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply index access to the current value if it's a list.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing the value at the given index
        """
        if isinstance(current, list):
            idx = self.index if self.index >= 0 else len(current) + self.index
            if 0 <= idx < len(current):
                yield from self._traverse(current[idx], remainingPath, contexts)
        else:
            yield from self._traverse(current, remainingPath, contexts)


class Slice(JsonPath):
    """Path element that accesses a slice of list items."""

    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[JsonPath] = None) -> None:
        """Initiates the slice path.

        Args:
            start (Optional[int]): the start index of the slice (inclusive)
            end (Optional[int]): the end index of the slice (exclusive)
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply slice access to a list.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing the values in the sliced range
        """
        if isinstance(current, list):
            start = self.start or 0
            end = self.end if self.end is not None else len(current)
            if start < 0:
                start += len(current)
            if end < 0:
                end += len(current)
            for item in current[start:end]:
                yield from self._traverse(item, remainingPath, contexts)
        else:
            yield from self._traverse(current, remainingPath, contexts)


class KeyContextAndValue(JsonPath):
    """Path element that iterates through all dictionary key-value pairs."""

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Iterate over all key-value pairs in a dictionary, appending the key to the context stack.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing each dictionary value
        """
        if isinstance(current, dict):
            for key, value in current.items():
                yield from self._traverse(value, remainingPath, contexts + [key])
        else:
            yield from self._traverse(current, remainingPath, contexts)


class AddedContext(JsonPath):
    """Path element that adds the current value to the context."""

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Appends the current value to the context before continuing traversal.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: the result of continuing traversal with updated context
        """
        yield from self._traverse(current, remainingPath, contexts + [current])


class MultiValue(JsonPath):
    """Path element that collects values from multiple sub-paths."""
    
    def __init__(self, paths: tuple[JsonPath], prevPath: Optional[JsonPath] = None) -> None:
        """Initiates the multivalue path.
        
        Args:
            paths (tuple[JsonPath]): a tuple of sub-paths to evaluate from the current value
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.paths = paths
    
    def _apply(self, current: Any, _: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Evaluate each sub-path from the current value and yield combined context + results.
        
        Args:
            current (Any): the current value being evaluated
            _ (list[JsonPath]): unused because multivalue is terminal
            contexts (list[Any]): the current context stack
        
        Yields:
            list[Any]: the context list followed by the results from each sub-path
        """
        # Collect all results from each sub-path
        allResults = []
        for path in self.paths:
            pathResults = list(path.walk(current))
            allResults.append(pathResults)
        
        # Create Cartesian product of all sub-path results
        for combination in itertools.product(*allResults):
            yield contexts + list(combination)
