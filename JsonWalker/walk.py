import itertools
from typing import (
    Generator, Any, Optional, Callable, TypeVar, Generic,
    Union, Type, cast, overload
)

"""A note to future developers- trying to split this up into multiple files is not a good idea, despite its length, 
because the ways to deal with circular dependencies break static type inference. 

That is something we REALLY do not want to do.
"""

# --- Type Variables ---
TypeForJsonLikeData = Union[dict[str, Any], list[Any]]
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

# --- Core classes ---
class _Executor(Generic[T]):
    """Core path execution functionality - handles walking and traversing paths.\n
    This is the base class that provides the fundamental path execution logic for traversing
    JSON-like data structures. It maintains a chain of path segments and provides methods
    to execute the complete path query.
    """
    
    def __init__(self, prevPath: Optional['_Executor[Any]'] = None) -> None:
        """Initialize the executor with an optional previous path segment.
        
        Args:
            prevPath (Optional[_Executor[Any]], optional): the previous path segment in the chain; defaults to None
        """
        self._prevPath = prevPath

    def walk(self, data: TypeForJsonLikeData) -> Generator[T, None, None]:
        """Execute the path query on the given JSON-like data.\n
        This is the main entry point for executing a complete path query. It builds the full path
        by following the chain of path segments and then traverses the data structure accordingly.
        
        Args:
            data (TypeForJsonLikeData): the JSON-like data structure (dict or list) to traverse
            
        Yields:
            T: each matching result found by traversing the path through the data
        """
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _getFullPath(self) -> list['_Executor[Any]']:
        """Build the complete path by following the chain backwards.\n
        Constructs the full path by traversing the linked list of path segments from the current
        segment back to the root, then reverses the order to get the correct execution sequence.
        
        Returns:
            list[_Executor[Any]]: the complete path as a list of executor segments in execution order
        """
        path: list['_Executor[Any]'] = []
        current: Optional['_Executor[Any]'] = self
        while current:
            path.insert(0, current)
            current = current._prevPath
        return path

    def _traverse(self, current: Any, remainingPath: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Recursively traverse the data structure according to the path.\n
        This method handles the recursive traversal of the data structure, applying each path segment
        in sequence. When no path segments remain, it yields the final result.
        
        Args:
            current (Any): the current data element being processed
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply  
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from applying the path to the current data
        """
        if current is None:
            return

        if not remainingPath:
            finalResult = contexts + [current] if contexts else current
            yield cast(T, finalResult)
            return

        pathItem = remainingPath[0]
        yield from pathItem._apply(current, remainingPath[1:], contexts.copy())

    def _apply(self, current: Any, remainingPath: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply this path item to the current data and continue traversal.\n
        This is the default implementation that simply continues traversal without modification.
        Subclasses override this method to implement specific path segment behavior.
        
        Args:
            current (Any): the current data element being processed
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from continuing the traversal
        """
        yield from self._traverse(current, remainingPath, contexts)


class _Builder:
    """Path building functionality - creates new path segments.\n
    This class provides methods to construct various types of path segments that can be chained
    together to create complex queries for traversing JSON-like data structures.
    """
    
    def key(self, keyName: str, default: Any = None) -> "_KeyPath[Any]":
        """Creates a path segment that accesses a dictionary by a specific key.
        
        Args:
            keyName (str): the dictionary key to access
            default (Any, optional): the default value to use if the key is not found; defaults to None
            
        Returns:
            _KeyPath[Any]: a path segment that accesses the specified dictionary key
        """
        return _KeyPath(keyName, default, self)

    def listIndex(self, index: int) -> "_IndexPath[Any]":
        """Creates a path segment that accesses a specific index in a list.
        
        Args:
            index (int): the list index to access (supports negative indexing)
            
        Returns:
            _IndexPath[Any]: a path segment that accesses the specified list index
        """
        return _IndexPath(index, self)

    def listSlice(self, start: Optional[int] = None, end: Optional[int] = None) -> "_SlicePath[Any]":
        """Creates a path segment that accesses a range of elements in a list.
        
        Args:
            start (Optional[int], optional): the starting index of the slice; defaults to None (beginning)
            end (Optional[int], optional): the ending index of the slice; defaults to None (end)
            
        Returns:
            _SlicePath[Any]: a path segment that accesses the specified slice of list elements
        """
        return _SlicePath(start, end, self)

    def listAll(self) -> "_SlicePath[Any]":
        """Creates a path segment that accesses all elements in a list.\n
        This is equivalent to listSlice() with no parameters, accessing the entire list.
        
        Returns:
            _SlicePath[Any]: a path segment that accesses all elements in a list
        """
        return _SlicePath(None, None, self)

    def yieldKey(self, valuePath: _Executor[U]) -> "_YieldedKeyPlusValuePath[tuple[str, U]]":
        """Creates a path that yields (key, value) pairs from dictionary iteration.\n
        This method creates a terminal path segment that iterates over dictionary key-value pairs,
        applying the provided value path to each value and yielding (key, result) tuples.
        
        Args:
            valuePath (_Executor[U]): the path to apply to each dictionary value
            
        Returns:
            _YieldedKeyPlusValuePath[tuple[str, U]]: a terminal path that yields (key, value) pairs
        """
        return _YieldedKeyPlusValuePath(valuePath, self)

    def filter(self, conditionPath: _Executor[Any], condition: Callable[[Any], bool]) -> "_FilteredPath[T]":
        """Creates a path segment that filters results based on a condition.
        
        Args:
            conditionPath (_Executor[Any]): the path to evaluate for the filter condition
            condition (Callable[[Any], bool]): a function that takes a value and returns True to include it
            
        Returns:
            _FilteredPath[T]: a path segment that filters based on the provided condition
        """
        return _FilteredPath(conditionPath, condition, self)

    def ensureType(self, expectedType: Type[U]) -> "_EnsureTypePath[U]":
        """Creates a path segment that ensures the current value is of a specific type.\n
        This creates a terminal path segment that only yields values if they match the expected type.
        
        Args:
            expectedType (Type[U]): the type that the current value must match
            
        Returns:
            _EnsureTypePath[U]: a terminal path that ensures type matching
        """
        return _EnsureTypePath(expectedType, self)

    # Multi method overloads
    @overload
    def multi(self, path1: _Executor[U]) -> "_MultiValuePath[tuple[U]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V]) -> "_MultiValuePath[tuple[U, V]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W]) -> "_MultiValuePath[tuple[U, V, W]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X]) -> "_MultiValuePath[tuple[U, V, W, X]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y]) -> "_MultiValuePath[tuple[U, V, W, X, Y]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1], path8: _Executor[A2]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1], path8: _Executor[A2], path9: _Executor[A3]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1], path8: _Executor[A2], path9: _Executor[A3], path10: _Executor[A4]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1], path8: _Executor[A2], path9: _Executor[A3], path10: _Executor[A4], path11: _Executor[A5]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5]]": ...
    @overload
    def multi(self, path1: _Executor[U], path2: _Executor[V], path3: _Executor[W], path4: _Executor[X], path5: _Executor[Y], path6: _Executor[Z], path7: _Executor[A1], path8: _Executor[A2], path9: _Executor[A3], path10: _Executor[A4], path11: _Executor[A5], path12: _Executor[A6]) -> "_MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5, A6]]": ...
    # Default for 13+ paths (no type hinting)
    def multi(self, *paths: 'JsonPath[Any]') -> "_MultiValuePath[tuple[Any, ...]]":
        """Creates a path segment that collects multiple values from different sub-paths.\n
        This creates a terminal path segment that evaluates multiple sub-paths from the current point
        and returns all combinations of their results as tuples. This is useful for extracting
        multiple related values from the same data structure.

        Args:
            *paths (JsonPath): one or more sub-paths to evaluate from the current point

        Returns:
            _MultiValuePath: A terminal path segment that gathers values from each of the provided paths
        """
        return _MultiValuePath(paths, self)


# --- class to begin a path ---
class JsonPath(_Executor[T], _Builder):
    """Main JsonPath class to start a path.\n
    This is the primary entry point for creating JsonPath queries. It combines the execution
    capabilities of _Executor with the building capabilities of _Builder to provide a complete
    path construction and execution system.
    
    Example:
        path = JsonPath().key("users").listAll().key("name")
        results = list(path.walk(data))
    """
    pass


# --- Parent classes to all path classes---
class _TerminalPath(_Executor[T]):
    """Base class for path segments that cannot continue building (terminal).\n
    Terminal path segments are the end points of a path chain. They perform their operation
    and cannot have additional path segments added to them. Examples include multi() and yieldKey().
    
    Args:
        prevPath (Optional[_Executor[Any]], optional): the previous path segment in the chain; defaults to None
    """
    pass


class _ContinuablePath(_Executor[T], _Builder):
    """Base class for path segments that can continue building (non-terminal).\n
    Continuable path segments can have additional path segments chained after them.
    They inherit from both _Executor (for execution) and _Builder (for continued building).
    """
    @overload
    def add(self, pathToAdd: _TerminalPath[U]) -> "_JoinedTerminalPath[U]": ...
    @overload
    def add(self, pathToAdd: "_ContinuablePath[U]") -> "_JoinedContinuablePath[U]": ...

    def add(self, pathToAdd: _Executor[U]) -> _Executor[U]:
        """Combines the current path with another path segment, returning a new path.\n
        This method provides an object-oriented way to chain path objects together. The return type 
        is inferred based on the path segment being added. If the added path is terminal 
        (e.g., multi() or yieldKey()), the resulting path cannot be extended further, and your 
        IDE will correctly reflect this.
        
        Args:
            path_to_add (_Executor[U]): the path segment to add to the current path
            
        Returns:
            _Executor[U]: a new joined path with the appropriate terminal/continuable type
        """
        isTerminal = isinstance(pathToAdd, _TerminalPath)
        combinedPath = self._combineTwoPaths(pathToAdd)

        if isTerminal:
            return _JoinedTerminalPath(combinedPath, pathToAdd)
        else:
            return _JoinedContinuablePath(combinedPath, pathToAdd)

    def _combineTwoPaths(self, second: _Executor[Any]) -> Optional[_Executor[Any]]:
        """Combine two paths into a single chained path.\n
        This method creates a new path by cloning all segments from both the current path
        and the second path, linking them together in the correct order.
        
        Args:
            second (_Executor[Any]): the second path to combine with the current path
            
        Returns:
            Optional[_Executor[Any]]: the combined path with all segments from both paths
        """
        combinedPath = None
        # Clone segments of the first path into combinedPath
        for segment in self._getFullPath():
            combinedPath = self._cloneSegment(segment, combinedPath)
        # Clone segments of the second path into combinedPath
        for segment in second._getFullPath():
            combinedPath = self._cloneSegment(segment, combinedPath)
        return combinedPath
    
    @staticmethod
    def _cloneSegment(segment: _Executor[Any], prevPath: Optional[_Executor[Any]]) -> _Executor[Any]:
        """Create a copy of a path segment with a new previous path.\n
        This method creates a deep copy of a path segment, preserving all its properties
        but linking it to a new previous path segment. This is essential for combining paths
        without modifying the original segments.
        
        Args:
            segment (_Executor[Any]): the path segment to clone
            prevPath (Optional[_Executor[Any]]): the new previous path to link to
            
        Returns:
            _Executor[Any]: a cloned copy of the segment with the new previous path
            
        Raises:
            TypeError: If the segment type is not recognized
        """
        if isinstance(segment, _KeyPath):
            return _KeyPath(segment.dictKey, segment.default, prevPath)
        elif isinstance(segment, _IndexPath):
            return _IndexPath(segment.index, prevPath)
        elif isinstance(segment, _SlicePath):
            return _SlicePath(segment.start, segment.end, prevPath)
        elif isinstance(segment, _YieldedKeyPlusValuePath):
            return _YieldedKeyPlusValuePath(segment.valuePath, prevPath)
        elif isinstance(segment, _MultiValuePath):
            return _MultiValuePath(segment.paths, prevPath)
        elif isinstance(segment, _FilteredPath):
            return _FilteredPath(segment.conditionPath, segment.condition, prevPath)
        elif isinstance(segment, _EnsureTypePath):
            return _EnsureTypePath(segment.expectedType, prevPath)
        elif isinstance(segment, (JsonPath, _ContinuablePath, _TerminalPath, _Executor)):
            return _Executor(prevPath)
        else:
            raise TypeError(f"Unknown path segment type: {type(segment)}")


# Non-terminal path segments (can continue building)
class _KeyPath(_ContinuablePath[Any]):
    """Path element that accesses a dictionary key.\n
    This path segment attempts to access a specified key from a dictionary. If the key
    is not found, it uses the provided default value.
    
    Args:
        key (str): the dictionary key to access
        default (Any, optional): the default value to use if the key is not found; defaults to None
        prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
    """

    def __init__(self, key: str, default: Any = None, prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the key path segment.
        
        Args:
            key (str): the dictionary key to access
            default (Any, optional): the default value to use if the key is not found; defaults to None
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.dictKey = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the key access operation to the current data.\n
        Attempts to access the specified key from the current data if it's a dictionary.
        If the key is not found, uses the default value.
        
        Args:
            current (Any): the current data element (should be a dictionary)
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with the accessed value
        """
        if isinstance(current, dict):
            value = current.get(self.dictKey, self.default)
            yield from self._traverse(value, remainingPath, contexts)


class _IndexPath(_ContinuablePath[Any]):
    """Path element that accesses a list by index.\n
    This path segment attempts to access a specific index from a list. It supports
    negative indexing and includes bounds checking.
    
    Args:
        index (int): the list index to access (supports negative indexing)
        prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
    """

    def __init__(self, index: int, prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the index path segment.
        
        Args:
            index (int): the list index to access (supports negative indexing)
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the index access operation to the current data.\n
        Attempts to access the specified index from the current data if it's a list.
        Includes bounds checking to prevent index errors.
        
        Args:
            current (Any): the current data element (should be a list)
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with the accessed element
        """
        if isinstance(current, list) and -len(current) <= self.index < len(current):
            yield from self._traverse(current[self.index], remainingPath, contexts)


class _SlicePath(_ContinuablePath[Any]):
    """Path element that accesses a slice of list items.\n
    This path segment accesses a range of elements from a list using Python's slice notation.
    It yields results for each element in the specified range.
    """
    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the slice path segment.
        
        Args:
            start (Optional[int]): the starting index of the slice; defaults to None (beginning)
            end (Optional[int]): the ending index of the slice; defaults to None (end)
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the slice operation to the current data.\n
        Accesses the specified slice of elements from the current data if it's a list.
        Yields results for each element in the slice.
        
        Args:
            current (Any): the current data element (should be a list)
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with each element in the slice
        """
        if isinstance(current, list):
            for item in current[self.start:self.end]:
                yield from self._traverse(item, remainingPath, contexts)


class _FilteredPath(_ContinuablePath[T]):
    """Path element that filters the current value based on a condition.\n
    This path segment evaluates a condition path against the current data and only
    continues traversal if the condition function returns True for any of the results.
    """
    def __init__(self, conditionPath: _Executor[Any], condition: Callable[[Any], bool], prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the filtered path segment.
        
        Args:
            conditionPath (_Executor[Any]): the path to evaluate for the filter condition
            condition (Callable[[Any], bool]): a function that takes a value and returns whether to filter in the path
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.conditionPath = conditionPath
        self.condition = condition
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the filter condition to the current data.\n
        Evaluates the condition path against the current data and only continues traversal
        if the condition function returns True for any of the results.
        
        Args:
            current (Any): the current data element to filter
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from continuing traversal if the condition is met
        """
        conditionResults = list(self.conditionPath.walk(current))
        if any(self.condition(res) for res in conditionResults):
            yield from self._traverse(current, remainingPath, contexts)


class _JoinedContinuablePath(_ContinuablePath[T]):
    """A joined path that can continue building (when final path is non-terminal).\n
    This class represents the result of combining two paths where the final path segment
    is continuable (non-terminal). It maintains the combined path structure while
    delegating execution logic to the template path.
    """
    def __init__(self, combinedPath: Optional[_Executor[Any]], templatePath: _Executor[T]) -> None:
        """Initialize the joined continuable path.
        
        Args:
            combinedPath (Optional[_Executor[Any]]): the combined path structure
            templatePath (_Executor[T]): the template path that defines the execution behavior
        """
        super().__init__(combinedPath)
        self._templatePath = templatePath
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the joined path operation using the template path's logic.\n
        Delegates the actual execution logic to the template path's _apply method.
        
        Args:
            current (Any): the current data element being processed
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from the template path's execution logic
        """
        yield from self._templatePath._apply(current, remainingPath, contexts)


# Terminal path segments (cannot continue building)
class _JoinedTerminalPath(_TerminalPath[T]):
    """A joined path that cannot continue building (when final path is terminal).\n
    This class represents the result of combining two paths where the final path segment
    is terminal. It maintains the combined path structure while delegating execution
    logic to the template path.
    """
    def __init__(self, combinedPath: Optional[_Executor[Any]], templatePath: _Executor[T]) -> None:
        """Initialize the joined terminal path.
        
        Args:
            combinedPath (Optional[_Executor[Any]]): the combined path structure
            templatePath (_Executor[T]): the template path that defines the execution behavior
        """
        super().__init__(combinedPath)
        self._templatePath = templatePath
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the joined path operation using the template path's logic.\n
        Delegates the actual execution logic to the template path's _apply method.
        
        Args:
            current (Any): the current data element being processed
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from the template path's execution logic
        """
        yield from self._templatePath._apply(current, remainingPath, contexts)


class _EnsureTypePath(_TerminalPath[T]):
    """Path element that ensures the current value is of a specific type.
    
    This path segment acts as a type filter, only continuing traversal if the current
    data element is an instance of the expected type. If the type check fails, no
    results are yielded.
    """
    def __init__(self, expectedType: Type[T], prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the type-checking path segment.
        
        Args:
            expectedType (Type[T]): the type that the current value must be an instance of
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.expectedType = expectedType
        
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the type check to the current data.
        
        Checks if the current data element is an instance of the expected type and only
        continues traversal if the type check passes.
        
        Args:
            current (Any): the current data element to type-check
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from continuing traversal if the type check passes
        """
        if isinstance(current, self.expectedType):
            yield from self._traverse(current, remainingPath, contexts)


class _YieldedKeyPlusValuePath(_TerminalPath[T]):
    """Path element that yields (key, value) pairs from dictionary iteration.
    
    This path segment iterates over dictionary items, applies a value path to each
    dictionary value, and yields tuples containing the key paired with each result
    from the value path traversal.
    """
    def __init__(self, valuePath: _Executor[Any], prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the key-value pair path segment.
        
        Args:
            valuePath (_Executor[Any]): the path to apply to each dictionary value
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.valuePath = valuePath
        
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the key-value pair extraction to the current data.
        
        Iterates over dictionary items, applies the value path to each value, and yields
        tuples of (key, valueResult) for each result from the value path traversal.
        
        Args:
            current (Any): the current data element (should be a dictionary)
            remainingPath (list[_Executor[Any]]): the remaining path segments to apply
            contexts (list[Any]): context information collected during traversal
            
        Yields:
            T: Results from continuing traversal with each (key, valueResult) tuple
        """
        if isinstance(current, dict):
            for key, value in current.items():
                valueResults = list(self.valuePath.walk(value))
                for result in valueResults:
                    keyValueTuple = (key, result)
                    yield from self._traverse(keyValueTuple, remainingPath, contexts)


class _MultiValuePath(_TerminalPath[T]):
    """Path element that collects values from multiple sub-paths.\n
    This path segment applies multiple paths to the current data and yields all possible
    combinations of their results as tuples. Each path is evaluated independently, and
    the Cartesian product of all path results is generated.
    """
    def __init__(self, paths: tuple[_Executor[Any], ...], prevPath: Optional[_Executor[Any]] = None) -> None:
        """Initialize the multi-value path segment.
        
        Args:
            paths (tuple[_Executor[Any], ...]): a tuple of paths to apply to the current data
            prevPath (Optional[_Executor[Any]], optional): the previous path segment; defaults to None
        """
        super().__init__(prevPath)
        self.paths = paths
    
    def _apply(self, current: Any, _: list[_Executor[Any]], __: list[Any]) -> Generator[T, None, None]:
        """Apply multiple paths and yield all combinations of their results.
        
        Evaluates each path against the current data, collects all results, and yields
        every possible combination of results as tuples. If a path yields no results,
        None is used as a placeholder in the combinations.
        
        Args:
            current (Any): the current data element to apply all paths to
            _ (list[_Executor[Any]]): unused remaining path segments (terminal path)
            __ (list[Any]): unused context information (terminal path)
            
        Yields:
            T: Each combination of results from all paths as a tuple
        """
        allResults = []
        for path in self.paths:
            pathResults = list(path.walk(current))
            allResults.append(pathResults if pathResults else [None])
        
        for combination in itertools.product(*allResults):
            yield cast(T, combination)
