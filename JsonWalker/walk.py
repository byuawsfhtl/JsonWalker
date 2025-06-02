from typing import Generator, Any, Optional

class JsonPath:
    """Base class for building chainable JSON path queries. Allows fluent querying of nested dictionaries and lists."""
    
    def __init__(self, prevPath: Optional['JsonPath'] = None):
        """Initialize a new JsonPath object.

        Args:
            prevPath (Optional[JsonPath]): The preceding path element in the chain.
        """
        self.prevPath = prevPath
        self.contexts: list[Any] = []

    def _getFullPath(self) -> list['JsonPath']:
        """Build the complete path by following the chain backwards.

        Returns:
            list[JsonPath]: List of JsonPath nodes representing the full query chain.
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
            data (dict | list): The JSON-styled data structure to walk.

        Yields:
            Any: Each matched element in the path.
        """
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _traverse(self, current: Any, remainingPath: list['JsonPath'], contexts: list[Any]) -> Generator[Any, None, None]:
        """Recursively traverse the data structure according to the path.

        Args:
            current (Any): The current data element being examined.
            remainingPath (list[JsonPath]): Remaining path elements to apply.
            contexts (list[Any]): Accumulated context values.

        Yields:
            Any: Final results after full traversal.
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
            current (Any): Current node in the JSON structure.
            remainingPath (list[JsonPath]): Path nodes left to apply.
            contexts (list[Any]): Context accumulated so far.

        Yields:
            Any: Traversal result.
        """
        yield from self._traverse(current, remainingPath, contexts)

    def key(self, keyName: str, default: Any = None) -> "Key":
        """Creates a path segment that accesses a dictionary by a specific key.

        Args:
            keyName (str): The key to access in the dictionary.
            default (Any, optional): A fallback value to use if the key is not found; defaults to None.

        Returns:
            Key: A `JsonPath` segment that retrieves the value associated with `keyName`.
        """
        return Key(keyName, default, self)

    def index(self, idx: int) -> "Index":
        """Creates a path segment that accesses a specific index in a list.

        Args:
            idx (int): The index to access in the list. Negative indices are supported.

        Returns:
            Index: A `JsonPath` segment that retrieves the item at the specified index.
        """
        return Index(idx, self)

    def slice(self, start: Optional[int] = None, end: Optional[int] = None) -> "Slice":
        """Creates a path segment that accesses a range of elements in a list.

        Args:
            start (Optional[int], optional): The starting index of the slice (inclusive). Defaults to None (start of list).
            end (Optional[int], optional): The ending index of the slice (exclusive). Defaults to None (end of list).

        Returns:
            Slice: A `JsonPath` segment that yields elements within the given slice range.
        """
        return Slice(start, end, self)

    def all(self) -> "Slice":
        """Creates a path segment that accesses all elements in a list.

        Equivalent to calling `slice()` with no arguments.

        Returns:
            Slice: A `JsonPath` segment that iterates over all items in a list.
        """
        return Slice(None, None, self)

    def items(self) -> "DictItems":
        """Creates a path segment that iterates through all key-value pairs in a dictionary.

        The keys are appended to the context, and the values are passed on to the next segment.

        Returns:
            DictItems: A `JsonPath` segment for dictionary iteration.
        """
        return DictItems(self)

    def addContext(self) -> "AdditionalContext":
        """Creates a path segment that adds the current value to the context.

        Useful for collecting intermediate values during path evaluation.

        Returns:
            AdditionalContext: A `JsonPath` segment that augments the context with the current value.
        """
        return AdditionalContext(self)

    def multi(self, *paths: 'JsonPath') -> "MultiValue":
        """Creates a path segment that collects multiple values from different sub-paths.

        Args:
            *paths (JsonPath): One or more sub-paths to evaluate from the current point.

        Returns:
            MultiValue: A `JsonPath` segment that gathers values from each of the provided paths.
        """
        return MultiValue(paths, self)


class Key(JsonPath):
    """Path element that accesses a dictionary key."""

    def __init__(self, key: str, default: Any = None, prevPath: Optional[JsonPath] = None):
        """Initiates the key path.

        Args:
            key (str): The dictionary key to access.
            default (Any, optional): A fallback value if the key is not found. Defaults to None.
            prevPath (Optional[JsonPath]): The preceding path segment. Defaults to None.
        """
        super().__init__(prevPath)
        self.key = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Applies the key lookup on a dictionary.
        If the current object is a dictionary, retrieve the value for the specified key.
        If not, skip key lookup and pass through the object unchanged.

        Args:
            current (Any): The current value being traversed.
            remainingPath (list[JsonPath]): Remaining path segments to apply.
            contexts (list[Any]): The current context stack.

        Yields:
            Any: Results from traversing the matched value.
        """
        if isinstance(current, dict):
            value = current.get(self.key, self.default)
            yield from self._traverse(value, remainingPath, contexts)
        else:
            yield from self._traverse(current, remainingPath, contexts)


class Index(JsonPath):
    """Path element that accesses a list by index."""

    def __init__(self, index: int, prevPath: Optional[JsonPath] = None):
        """Initiates the index path.

        Args:
            index (int): The list index to access (supports negative indices).
            prevPath (Optional[JsonPath]): The preceding path segment. Defaults to None.
        """
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply index access to the current value if it's a list.

        Args:
            current (Any): The current value being traversed.
            remainingPath (list[JsonPath]): Remaining path segments to apply.
            contexts (list[Any]): The current context stack.

        Yields:
            Any: Results from traversing the value at the given index.
        """
        if isinstance(current, list):
            idx = self.index if self.index >= 0 else len(current) + self.index
            if 0 <= idx < len(current):
                yield from self._traverse(current[idx], remainingPath, contexts)
        else:
            yield from self._traverse(current, remainingPath, contexts)


class Slice(JsonPath):
    """Path element that accesses a slice of list items."""

    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[JsonPath] = None):
        """Initiates the slice path.

        Args:
            start (Optional[int]): The start index of the slice (inclusive).
            end (Optional[int]): The end index of the slice (exclusive).
            prevPath (Optional[JsonPath]): The preceding path segment. Defaults to None.
        """
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply slice access to a list.

        Args:
            current (Any): The current value being traversed.
            remainingPath (list[JsonPath]): Remaining path segments to apply.
            contexts (list[Any]): The current context stack.

        Yields:
            Any: Results from traversing the values in the sliced range.
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


class DictItems(JsonPath):
    """Path element that iterates through all dictionary key-value pairs."""

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Iterate over all key-value pairs in a dictionary, appending the key to the context stack.

        Args:
            current (Any): The current value being traversed.
            remainingPath (list[JsonPath]): Remaining path segments to apply.
            contexts (list[Any]): The current context stack.

        Yields:
            Any: Results from traversing each dictionary value.
        """
        if isinstance(current, dict):
            for key, value in current.items():
                yield from self._traverse(value, remainingPath, contexts + [key])
        else:
            yield from self._traverse(current, remainingPath, contexts)


class AdditionalContext(JsonPath):
    """Path element that adds the current value to the context."""

    def _apply(self, current: Any, remainingPath: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Appends the current value to the context before continuing traversal.

        Args:
            current (Any): The current value being traversed.
            remainingPath (list[JsonPath]): Remaining path segments to apply.
            contexts (list[Any]): The current context stack.

        Yields:
            Any: The result of continuing traversal with updated context.
        """
        yield from self._traverse(current, remainingPath, contexts + [current])


class MultiValue(JsonPath):
    """Path element that collects values from multiple sub-paths."""

    def __init__(self, paths: tuple[JsonPath], prevPath: Optional[JsonPath] = None):
        """Initiates the multivalue path.

        Args:
            paths (tuple[JsonPath]): A tuple of sub-paths to evaluate from the current value.
            prevPath (Optional[JsonPath]): The preceding path segment. Defaults to None.
        """
        super().__init__(prevPath)
        self.paths = paths

    def _apply(self, current: Any, _: list[JsonPath], contexts: list[Any]) -> Generator[Any, None, None]:
        """Evaluate each sub-path from the current value and yield combined context + results.

        Args:
            current (Any): The current value being evaluated.
            _ (list[JsonPath]): Unused; MultiValue is terminal.
            contexts (list[Any]): The current context stack.

        Yields:
            list[Any]: The context list followed by the results from each sub-path.
        """
        values = [list(path.walk(current))[0] for path in self.paths if list(path.walk(current))]
        yield contexts + values


def jsonPath() -> JsonPath:
    """Start a new JSON path query chain.

    Returns:
        JsonPath: A root JsonPath object.
    """
    return JsonPath()


# Usage examples
if __name__ == "__main__":
    # Example JSON data
    data = {
        "key1": [
            {
                "key2": 100
            },
            {}
        ]
    }
    
    # Example 1: Simple path with context
    # Equivalent to: 'key1[*]^ | key2(-1;int)'
    path = jsonPath().key("key1").all().addContext().key("key2", default=-1)
    for key1_val, key2 in path.walk(data):
        print(f"key1_val: {key1_val}, key2: {key2}")
    print('--------------------------------------')
    

    # Example 2: Multi-value return
    # Equivalent to: 'key1 | key2 | item1, item2'
    data2 = {
        "key1": {
            "key2": {
                "item1": "hello",
                "item2": "world"
            }
        }
    }
    path = jsonPath().key("key1").addContext().key("key2").multi(
        jsonPath().key("item1"),
        jsonPath().key("item2")
    )    
    for context, item1, item2 in path.walk(data2):
        print(f"{item1} {item2}")
    print('--------------------------------------')
    
    
    # Example 3: dictionary iteration
    # Equivalent to: 'key1{*}'
    data3 = {
        "key1": {
            "key2": "value2",
            "key3": "value3",
            "key4": "value4"
        }
    }
    path = jsonPath().key("key1").items()
    for key, value in path.walk(data3):
        print(f"{key} -- {value}")