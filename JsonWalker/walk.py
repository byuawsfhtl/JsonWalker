import itertools
from typing import (
    Generator, Any, Optional, Callable, TypeVar, Generic,
    Union, Type, cast, overload
)

# --- Type Variables ---
T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')
Y = TypeVar('Y')
Z = TypeVar('Z')
A1 = TypeVar('A1')
A2 = TypeVar('A2')
A3 = TypeVar('A3')
A4 = TypeVar('A4')
A5 = TypeVar('A5')
A6 = TypeVar('A6')

TypeForJsonLikeData = Union[dict[str, Any], list[Any]]

class JsonPath(Generic[T]):
    """Base class for building chainable JSON path queries with type inference."""
    
    def __init__(self, prevPath: Optional['JsonPath[Any]'] = None) -> None:
        """Initialize a new JsonPath object.

        Args:
            prevPath (Optional[JsonPath]): the preceding path element in the chain
        """
        self.prevPath = prevPath

    def _getFullPath(self) -> list['JsonPath[Any]']:
        """Build the complete path by following the chain backwards.

        Returns:
            list[JsonPath]: the full query chain of JsonPath nodes
        """
        path: list['JsonPath[Any]'] = []
        current: Optional['JsonPath[Any]'] = self
        while current:
            path.insert(0, current)
            current = current.prevPath
        return path

    def walk(self, data: TypeForJsonLikeData) -> Generator[T, None, None]:
        """Execute the path query on the given JSON-like data.

        Args:
            data (dict | list): the JSON-styled data structure to walk

        Yields:
            T: each matched element in the path
        """
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _traverse(self, current: Any, remainingPath: list['JsonPath[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Recursively traverse the data structure according to the path.

        Args:
            current (Any): the current data element being examined
            remainingPath (list[JsonPath]): remaining path elements to apply
            contexts (list[Any]): accumulated context values

        Yields:
            T: final results after full traversal
        """
        if current is None:
            return

        if not remainingPath:
            # If context was collected, yield it with the final value
            # Otherwise, just yield the value itself
            final_result = contexts + [current] if contexts else current
            yield cast(T, final_result)
            return

        pathItem = remainingPath[0]
        yield from pathItem._apply(current, remainingPath[1:], contexts.copy())

    def _apply(self, current: Any, remainingPath: list['JsonPath[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply this path item to the current data and continue traversal.

        Args:
            current (Any): current node in the JSON structure
            remainingPath (list[JsonPath]): path nodes left to apply
            contexts (list[Any]): context accumulated so far

        Yields:
            T: traversal result
        """
        yield from self._traverse(current, remainingPath, contexts)

    def key(self, keyName: str, default: Any = None) -> "Key[Any]":
        """Creates a path segment that accesses a dictionary by a specific key.

        Args:
            keyName (str): the key to access in the dictionary
            default (Any, optional): a fallback value to use if the key is not found; defaults to None

        Returns:
            Key: a JsonPath segment that retrieves the value associated with keyName
        """
        return Key(keyName, default, self)

    def listIndex(self, idx: int) -> "Index[Any]":
        """Creates a path segment that accesses a specific index in a list.

        Args:
            idx (int): the index to access in the list. Negative indices are supported

        Returns:
            Index: a JsonPath segment that retrieves the item at the specified index
        """
        return Index(idx, self)

    def listSlice(self, start: Optional[int] = None, end: Optional[int] = None) -> "Slice[Any]":
        """Creates a path segment that accesses a range of elements in a list.

        Args:
            start (Optional[int], optional): the starting index of the slice (inclusive). Defaults to None (start of list)
            end (Optional[int], optional): the ending index of the slice (exclusive). Defaults to None (end of list)

        Returns:
            Slice: a JsonPath segment that yields elements within the given slice range
        """
        return Slice(start, end, self)

    def listAll(self) -> "Slice[Any]":
        """Creates a path segment that accesses all elements in a list.

        Returns:
            Slice: a JsonPath segment that iterates over all items in a list
        """
        return Slice(None, None, self)

    def keyContextAndValue(self) -> "KeyContextAndValue[T]":
        """Adds dict keys to context and passes values to the next segment.
        The final type `T` depends on what follows this step.

        Returns:
            KeyContextAndValue: a JsonPath segment for dictionary iteration
        """
        return KeyContextAndValue(self)

    def addContext(self) -> "AddedContext[T]":
        """Creates a path segment that adds the current value to the context.
        Useful for collecting intermediate values during path evaluation.

        Returns:
            AddedContext: a JsonPath segment that augments the context with the current value
        """
        return AddedContext(self)

    # Multi method overloads for type inference for up to 12 paths (this way of doing things takes into account earlier versions of python)
    @overload
    def multi(self, path1: 'JsonPath[U]') -> "MultiValue[tuple[U]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]') -> "MultiValue[tuple[U, V]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]') -> "MultiValue[tuple[U, V, W]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]') -> "MultiValue[tuple[U, V, W, X]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]') -> "MultiValue[tuple[U, V, W, X, Y]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]') -> "MultiValue[tuple[U, V, W, X, Y, Z]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]', path8: 'JsonPath[A2]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]', path8: 'JsonPath[A2]', path9: 'JsonPath[A3]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]', path8: 'JsonPath[A2]', path9: 'JsonPath[A3]', path10: 'JsonPath[A4]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]', path8: 'JsonPath[A2]', path9: 'JsonPath[A3]', path10: 'JsonPath[A4]', path11: 'JsonPath[A5]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5]]": ...
    @overload
    def multi(self, path1: 'JsonPath[U]', path2: 'JsonPath[V]', path3: 'JsonPath[W]', path4: 'JsonPath[X]', path5: 'JsonPath[Y]', path6: 'JsonPath[Z]', path7: 'JsonPath[A1]', path8: 'JsonPath[A2]', path9: 'JsonPath[A3]', path10: 'JsonPath[A4]', path11: 'JsonPath[A5]', path12: 'JsonPath[A6]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5, A6]]": ...

    # Default for 13+ paths (no type hinting)
    def multi(self, *paths: 'JsonPath[Any]') -> "MultiValue[tuple[Any, ...]]":
        """Creates a path segment that collects multiple values from different sub-paths

        Args:
            *paths (JsonPath): one or more sub-paths to evaluate from the current point

        Returns:
            MultiValue: a JsonPath segment that gathers values from each of the provided paths
        """
        return MultiValue(paths, self)

    def filter(self, conditionPath: 'JsonPath[Any]', condition: Callable[[Any], bool]) -> "Filter[T]":
        """Creates a path segment that filters results based on a condition evaluated on a related path.
        
        The condition path is evaluated from the same parent context, but doesn't become part of 
        the main traversal path. Only items that satisfy the condition continue in the main path.

        Args:
            conditionPath (JsonPath): the path to evaluate for the filtering condition
            condition (Callable[[Any], bool]): a function that takes a value and returns True/False

        Returns:
            Filter: a JsonPath segment that filters based on the condition
        """
        return Filter(conditionPath, condition, self)

    def ensureType(self, expected_type: Type[U]) -> "EnsureType[U]":
        """Creates a path segment that ensures the current value is of a specific type.
        Values that don't match the expected type are filtered out.

        Args:
            expected_type (Type[U]): the expected type for the value

        Returns:
            EnsureType: a JsonPath segment that only yields values of the expected type
        """
        return EnsureType(expected_type, self)


class Key(JsonPath[Any]):
    """Path element that accesses a dictionary key."""

    def __init__(self, key: str, default: Any = None, prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the key path.

        Args:
            key (str): the dictionary key to access
            default (Any, optional): a fallback value if the key is not found; defaults to None
            prevPath (Optional[JsonPath]): the preceding path segment; defaults to None
        """
        super().__init__(prevPath)
        self.dictKey = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Applies the key lookup on a dictionary.

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

class Index(JsonPath[Any]):
    """Path element that accesses a list by index."""

    def __init__(self, index: int, prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the index path.

        Args:
            index (int): the list index to access (supports negative indices)
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply index access to the current value if it's a list.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing the value at the given index
        """
        if isinstance(current, list) and -len(current) <= self.index < len(current):
            yield from self._traverse(current[self.index], remainingPath, contexts)


class Slice(JsonPath[Any]):
    """Path element that accesses a slice of list items."""

    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the slice path.

        Args:
            start (Optional[int]): the start index of the slice (inclusive)
            end (Optional[int]): the end index of the slice (exclusive)
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply slice access to a list.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            Any: results from traversing the values in the sliced range
        """
        if isinstance(current, list):
            for item in current[self.start:self.end]:
                yield from self._traverse(item, remainingPath, contexts)


class KeyContextAndValue(JsonPath[T]):
    """Path element that iterates through all dictionary key-value pairs."""

    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Iterate over all key-value pairs in a dictionary, appending the key to the context stack.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            tuple[str, Any]: results from traversing each dictionary value
        """
        if isinstance(current, dict):
            for key, value in current.items():
                yield from self._traverse(value, remainingPath, contexts + [key])
        else:
            yield from self._traverse(current, remainingPath, contexts)


class AddedContext(JsonPath[T]):
    """Path element that adds the current value to the context."""

    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Appends the current value to the context before continuing traversal.

        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack

        Yields:
            T: the result of continuing traversal with updated context
        """
        yield from self._traverse(current, remainingPath, contexts + [current])


class MultiValue(JsonPath[T]):
    """Path element that collects values from multiple sub-paths."""
    
    def __init__(self, paths: tuple[JsonPath[Any], ...], prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the multivalue path.
        
        Args:
            paths (tuple[JsonPath]): a tuple of sub-paths to evaluate from the current value
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.paths = paths
    
    def _apply(self, current: Any, _: list[JsonPath[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Evaluate each sub-path from the current value and yield combined context + results.
        
        Args:
            current (Any): the current value being evaluated
            _ (list[JsonPath]): unused because multivalue is terminal
            contexts (list[Any]): the current context stack
        
        Yields:
            T: the context list followed by the results from each sub-path
        """
        allResults = []
        for path in self.paths:
            path_results = list(path.walk(current))
            # If no results, use [None] to ensure we still get a combination
            allResults.append(path_results if path_results else [None])
        
        for combination in itertools.product(*allResults):
            yield cast(T, combination)


class Filter(JsonPath[T]):
    """Path element that filters the current value based on a condition evaluated on a related path."""
    
    def __init__(self, conditionPath: JsonPath[Any], condition: Callable[[Any], bool], prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the filter path.
        
        Args:
            conditionPath (JsonPath): the path to evaluate for the filtering condition
            condition (Callable[[Any], bool]): a function that takes a value and returns True/False
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.conditionPath = conditionPath
        self.condition = condition
    
    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the filter by evaluating the condition path and only continuing if the condition is met.
        
        Args:
            current (Any): the current value being traversed (the parent context for both paths)
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack
        
        Yields:
            T: results from continuing the main path, but only if the condition is satisfied
        """
        conditionResults = list(self.conditionPath.walk(current))
        if any(self.condition(res) for res in conditionResults):
            yield from self._traverse(current, remainingPath, contexts)


class EnsureType(JsonPath[T]):
    """Path element that ensures the current value is of a specific type."""
    
    def __init__(self, expected_type: Type[T], prevPath: Optional[JsonPath[Any]] = None) -> None:
        """Initiates the ensure type path.
        
        Args:
            expected_type (Type[T]): the expected type for the value
            prevPath (Optional[JsonPath]): the preceding path segment. Defaults to None
        """
        super().__init__(prevPath)
        self.expected_type = expected_type
    
    def _apply(self, current: Any, remainingPath: list[JsonPath[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Only continue traversal if the current value matches the expected type.
        
        Args:
            current (Any): the current value being traversed
            remainingPath (list[JsonPath]): remaining path segments to apply
            contexts (list[Any]): the current context stack
        
        Yields:
            T: results from continuing traversal, but only if type matches
        """
        if isinstance(current, self.expected_type):
            yield from self._traverse(current, remainingPath, contexts)


class PathJoin(JsonPath[T]):
    """Path element that joins multiple paths together by combining their path segments."""
    
    def __init__(self, *paths: JsonPath[Any]) -> None:
        """Initiates the path join by combining the path segments from all provided paths.
        
        Args:
            *paths (JsonPath): variable number of paths to join together in order
        """
        if not paths:
            raise ValueError("PathJoin requires at least one path")
        
        # Combine all paths into a single chain
        combinedPath = self._combinePaths(paths)
        
        # Initialize this PathJoin as the final segment in the combined path
        super().__init__(combinedPath)
    
    def _combinePaths(self, paths: tuple[JsonPath[Any], ...]) -> Optional[JsonPath[Any]]:
        """Helper function to combine multiple paths into a single chained path.
        
        Args:
            paths (tuple[JsonPath, ...]): the paths to combine in order
            
        Returns:
            Optional[JsonPath]: the final segment of the combined path, or None if no paths
        """
        # Start with None (no previous path)
        combinedPath = None
        
        # Process each path in order
        for path in paths:
            combinedPath = self._appendPath(combinedPath, path)
        
        return combinedPath
    
    def _appendPath(self, currentPath: Optional[JsonPath[Any]], pathToAppend: JsonPath[Any]) -> Optional[JsonPath[Any]]:
        """Helper function to append one path to another.
        
        Args:
            currentPath (Optional[JsonPath]): the current combined path (or None)
            pathToAppend (JsonPath): the path to append to the current path
            
        Returns:
            Optional[JsonPath]: the final segment after appending
        """
        # Get all segments from the path to append
        segmentsToAppend = pathToAppend._getFullPath()
        
        # Add all segments from this path
        for segment in segmentsToAppend:
            # Create a new instance of the same type with the current path as previous
            newSegment = self._cloneSegment(segment, currentPath)
            currentPath = newSegment
        
        return currentPath
    
    def _cloneSegment(self, segment: JsonPath[Any], prevPath: Optional[JsonPath[Any]]) -> JsonPath[Any]:
        """Create a copy of a path segment with a new previous path.
        
        Args:
            segment (JsonPath): the segment to clone
            prevPath (Optional[JsonPath]): the new previous path
            
        Returns:
            JsonPath: a new instance of the same segment type
        """
        if isinstance(segment, Key):
            return Key(segment.dictKey, segment.default, prevPath)
        elif isinstance(segment, Index):
            return Index(segment.index, prevPath)
        elif isinstance(segment, Slice):
            return Slice(segment.start, segment.end, prevPath)
        elif isinstance(segment, KeyContextAndValue):
            return KeyContextAndValue(prevPath)
        elif isinstance(segment, AddedContext):
            return AddedContext(prevPath)
        elif isinstance(segment, MultiValue):
            return MultiValue(segment.paths, prevPath)
        elif isinstance(segment, Filter):
            return Filter(segment.conditionPath, segment.condition, prevPath)
        elif isinstance(segment, EnsureType):
            return EnsureType(segment.expected_type, prevPath)
        elif isinstance(segment, JsonPath):
            # Base JsonPath case
            newSegment = JsonPath(prevPath)
            return newSegment
        else:
            raise TypeError(f"Unknown path segment type: {type(segment)}")
