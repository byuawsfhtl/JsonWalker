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
TYPE_FOR_JSON_LIKE_DATA = Union[dict[str, Any], list[Any]]
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
    
    def __init__(self, prev_path: Optional['_Executor[Any]'] = None) -> None:
        """Initialize the executor with an optional previous path segment.
        
        Args:
            prev_path: the previous path segment in the chain; defaults to None
        """
        self._prev_path = prev_path

    def walk(self, data: TYPE_FOR_JSON_LIKE_DATA) -> Generator[T, None, None]:
        """Execute the path query on the given JSON-like data.\n
        This is the main entry point for executing a complete path query. It builds the full path
        by following the chain of path segments and then traverses the data structure accordingly.
        
        Args:
            data: the JSON-like data structure (dict or list) to traverse
            
        Yields:
            T: each matching result found by traversing the path through the data
        """
        path_items = self._getFullPath()
        yield from self._traverse(data, path_items, [])

    def _getFullPath(self) -> list['_Executor[Any]']:
        """Build the complete path by following the chain backwards.\n
        Constructs the full path by traversing the linked list of path segments from the current
        segment back to the root, then reverses the order to get the correct execution sequence.
        
        Returns:
            the complete path as a list of executor segments in execution order
        """
        path: list['_Executor[Any]'] = []
        current: Optional['_Executor[Any]'] = self
        while current:
            path.insert(0, current)
            current = current._prev_path
        return path

    def _traverse(self, current: Any, remaining_path: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Recursively traverse the data structure according to the path.\n
        This method handles the recursive traversal of the data structure, applying each path segment
        in sequence. When no path segments remain, it yields the final result.
        
        Args:
            current: the current data element being processed
            remaining_path: the remaining path segments to apply  
            contexts: context information collected during traversal
            
        Yields:
            T: Results from applying the path to the current data
        """
        if current is None:
            return

        if not remaining_path:
            final_result = contexts + [current] if contexts else current
            yield cast(T, final_result)
            return

        path_item = remaining_path[0]
        yield from path_item._apply(current, remaining_path[1:], contexts.copy())

    def _apply(self, current: Any, remaining_path: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply this path item to the current data and continue traversal.\n
        This is the default implementation that simply continues traversal without modification.
        Subclasses override this method to implement specific path segment behavior.
        
        Args:
            current: the current data element being processed
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from continuing the traversal
        """
        yield from self._traverse(current, remaining_path, contexts)


class _Builder:
    """Path building functionality - creates new path segments.\n
    This class provides methods to construct various types of path segments that can be chained
    together to create complex queries for traversing JSON-like data structures.
    """
    
    def key(self, key_name: str, default: Any = None) -> "_KeyPath[Any]":
        """Creates a path segment that accesses a dictionary by a specific key.
        
        Args:
            key_name: the dictionary key to access
            default: the default value to use if the key is not found; defaults to None
            
        Returns:
            a path segment that accesses the specified dictionary key
        """
        return _KeyPath(key_name, default, self)

    def list_index(self, index: int) -> "_IndexPath[Any]":
        """Creates a path segment that accesses a specific index in a list.
        
        Args:
            index: the list index to access (supports negative indexing)
            
        Returns:
            a path segment that accesses the specified list index
        """
        return _IndexPath(index, self)

    def list_slice(self, start: Optional[int] = None, end: Optional[int] = None) -> "_SlicePath[Any]":
        """Creates a path segment that accesses a range of elements in a list.
        
        Args:
            start: the starting index of the slice; defaults to None (beginning)
            end: the ending index of the slice; defaults to None (end)
            
        Returns:
            a path segment that accesses the specified slice of list elements
        """
        return _SlicePath(start, end, self)

    def list_all(self) -> "_SlicePath[Any]":
        """Creates a path segment that accesses all elements in a list.\n
        This is equivalent to listSlice() with no parameters, accessing the entire list.
        
        Returns:
            a path segment that accesses all elements in a list
        """
        return _SlicePath(None, None, self)

    def yield_key(self, value_path: _Executor[U]) -> "_YieldedKeyPlusValuePath[tuple[str, U]]":
        """Creates a path that yields (key, value) pairs from dictionary iteration.\n
        This method creates a terminal path segment that iterates over dictionary key-value pairs,
        applying the provided value path to each value and yielding (key, result) tuples.
        
        Args:
            value_path: the path to apply to each dictionary value
            
        Returns:
            a terminal path that yields (key, value) pairs
        """
        return _YieldedKeyPlusValuePath(value_path, self)

    def filter(self, condition_path: _Executor[Any], condition: Callable[[Any], bool]) -> "_FilteredPath[T]":
        """Creates a path segment that filters results based on a condition.
        
        Args:
            condition_path: the path to evaluate for the filter condition
            condition: a function that takes a value and returns True to include it
            
        Returns:
            a path segment that filters based on the provided condition
        """
        return _FilteredPath(condition_path, condition, self)

    def ensure_type(self, expected_type: Type[U]) -> "_EnsureTypePath[U]":
        """Creates a path segment that ensures the current value is of a specific type.\n
        This creates a terminal path segment that only yields values if they match the expected type.
        
        Args:
            expected_type: the type that the current value must match
            
        Returns:
            a terminal path that ensures type matching
        """
        return _EnsureTypePath(expected_type, self)

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
            *paths: one or more sub-paths to evaluate from the current point

        Returns:
            A terminal path segment that gathers values from each of the provided paths
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
    """
    pass


class _ContinuablePath(_Executor[T], _Builder):
    """Base class for path segments that can continue building (non-terminal).\n
    Continuable path segments can have additional path segments chained after them.
    They inherit from both _Executor (for execution) and _Builder (for continued building).
    """
    @overload
    def add(self, path_to_add: _TerminalPath[U]) -> "_JoinedTerminalPath[U]": ...
    @overload
    def add(self, path_to_add: "_ContinuablePath[U]") -> "_JoinedContinuablePath[U]": ...

    def add(self, path_to_add: _Executor[U]) -> _Executor[U]:
        """Combines the current path with another path segment, returning a new path.\n
        This method provides an object-oriented way to chain path objects together. The return type 
        is inferred based on the path segment being added. If the added path is terminal 
        (e.g., multi() or yieldKey()), the resulting path cannot be extended further, and your 
        IDE will correctly reflect this.
        
        Args:
            path_to_add: the path segment to add to the current path
            
        Returns:
            a new joined path with the appropriate terminal/continuable type
        """
        is_terminal = isinstance(path_to_add, _TerminalPath)
        combined_path = self._combineTwoPaths(path_to_add)

        if is_terminal:
            return _JoinedTerminalPath(combined_path, path_to_add)
        else:
            return _JoinedContinuablePath(combined_path, path_to_add)

    def _combineTwoPaths(self, second: _Executor[Any]) -> Optional[_Executor[Any]]:
        """Combine two paths into a single chained path.\n
        This method creates a new path by cloning all segments from both the current path
        and the second path, linking them together in the correct order.
        
        Args:
            second: the second path to combine with the current path
            
        Returns:
            the combined path with all segments from both paths
        """
        combined_path = None
        # Clone segments of the first path into combined_path
        for segment in self._getFullPath():
            combined_path = self._cloneSegment(segment, combined_path)
        # Clone segments of the second path into combined_path
        for segment in second._getFullPath():
            combined_path = self._cloneSegment(segment, combined_path)
        return combined_path
    
    @staticmethod
    def _cloneSegment(segment: _Executor[Any], prev_path: Optional[_Executor[Any]]) -> _Executor[Any]:
        """Create a copy of a path segment with a new previous path.\n
        This method creates a deep copy of a path segment, preserving all its properties
        but linking it to a new previous path segment. This is essential for combining paths
        without modifying the original segments.
        
        Args:
            segment: the path segment to clone
            prev_path: the new previous path to link to
            
        Returns:
            a cloned copy of the segment with the new previous path
            
        Raises:
            TypeError: If the segment type is not recognized
        """
        if isinstance(segment, _KeyPath):
            return _KeyPath(segment.dict_key, segment.default, prev_path)
        elif isinstance(segment, _IndexPath):
            return _IndexPath(segment.index, prev_path)
        elif isinstance(segment, _SlicePath):
            return _SlicePath(segment.start, segment.end, prev_path)
        elif isinstance(segment, _YieldedKeyPlusValuePath):
            return _YieldedKeyPlusValuePath(segment.value_path, prev_path)
        elif isinstance(segment, _MultiValuePath):
            return _MultiValuePath(segment.paths, prev_path)
        elif isinstance(segment, _FilteredPath):
            return _FilteredPath(segment.condition_path, segment.condition, prev_path)
        elif isinstance(segment, _EnsureTypePath):
            return _EnsureTypePath(segment.expected_type, prev_path)
        elif isinstance(segment, (JsonPath, _ContinuablePath, _TerminalPath, _Executor)):
            return _Executor(prev_path)
        else:
            raise TypeError(f"Unknown path segment type: {type(segment)}")


# Non-terminal path segments (can continue building)
class _KeyPath(_ContinuablePath[Any]):
    """Path element that accesses a dictionary key.\n
    This path segment attempts to access a specified key from a dictionary. If the key
    is not found, it uses the provided default value.
    """

    def __init__(self, key: str, default: Any = None, prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the key path segment.
        
        Args:
            key: the dictionary key to access
            default: the default value to use if the key is not found; defaults to None
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.dict_key = key
        self.default = default

    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the key access operation to the current data.\n
        Attempts to access the specified key from the current data if it's a dictionary.
        If the key is not found, uses the default value.
        
        Args:
            current: the current data element (should be a dictionary)
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with the accessed value
        """
        if isinstance(current, dict):
            value = current.get(self.dict_key, self.default)
            yield from self._traverse(value, remaining_path, contexts)


class _IndexPath(_ContinuablePath[Any]):
    """Path element that accesses a list by index.\n
    This path segment attempts to access a specific index from a list. It supports
    negative indexing and includes bounds checking.
    """

    def __init__(self, index: int, prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the index path segment.
        
        Args:
            index: the list index to access (supports negative indexing)
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.index = index

    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the index access operation to the current data.\n
        Attempts to access the specified index from the current data if it's a list.
        Includes bounds checking to prevent index errors.
        
        Args:
            current: the current data element (should be a list)
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with the accessed element
        """
        if isinstance(current, list) and -len(current) <= self.index < len(current):
            yield from self._traverse(current[self.index], remaining_path, contexts)


class _SlicePath(_ContinuablePath[Any]):
    """Path element that accesses a slice of list items.\n
    This path segment accesses a range of elements from a list using Python's slice notation.
    It yields results for each element in the specified range.
    """
    def __init__(self, start: Optional[int], end: Optional[int], prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the slice path segment.
        
        Args:
            start: the starting index of the slice; defaults to None (beginning)
            end: the ending index of the slice; defaults to None (end)
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        """Apply the slice operation to the current data.\n
        Accesses the specified slice of elements from the current data if it's a list.
        Yields results for each element in the slice.
        
        Args:
            current: the current data element (should be a list)
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            Any: Results from continuing traversal with each element in the slice
        """
        if isinstance(current, list):
            for item in current[self.start:self.end]:
                yield from self._traverse(item, remaining_path, contexts)


class _FilteredPath(_ContinuablePath[T]):
    """Path element that filters the current value based on a condition.\n
    This path segment evaluates a condition path against the current data and only
    continues traversal if the condition function returns True for any of the results.
    """
    def __init__(self, condition_path: _Executor[Any], condition: Callable[[Any], bool], prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the filtered path segment.
        
        Args:
            condition_path: the path to evaluate for the filter condition
            condition: a function that takes a value and returns whether to filter in the path
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.condition_path = condition_path
        self.condition = condition
    
    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the filter condition to the current data.\n
        Evaluates the condition path against the current data and only continues traversal
        if the condition function returns True for any of the results.
        
        Args:
            current: the current data element to filter
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from continuing traversal if the condition is met
        """
        condition_results = list(self.condition_path.walk(current))
        if any(self.condition(res) for res in condition_results):
            yield from self._traverse(current, remaining_path, contexts)


class _JoinedContinuablePath(_ContinuablePath[T]):
    """A joined path that can continue building (when final path is non-terminal).\n
    This class represents the result of combining two paths where the final path segment
    is continuable (non-terminal). It maintains the combined path structure while
    delegating execution logic to the template path.
    """
    def __init__(self, combined_path: Optional[_Executor[Any]], template_path: _Executor[T]) -> None:
        """Initialize the joined continuable path.
        
        Args:
            combined_path: the combined path structure
            template_path: the template path that defines the execution behavior
        """
        super().__init__(combined_path)
        self._template_path = template_path
    
    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the joined path operation using the template path's logic.\n
        Delegates the actual execution logic to the template path's _apply method.
        
        Args:
            current: the current data element being processed
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from the template path's execution logic
        """
        yield from self._template_path._apply(current, remaining_path, contexts)


# Terminal path segments (cannot continue building)
class _JoinedTerminalPath(_TerminalPath[T]):
    """A joined path that cannot continue building (when final path is terminal).\n
    This class represents the result of combining two paths where the final path segment
    is terminal. It maintains the combined path structure while delegating execution
    logic to the template path.
    """
    def __init__(self, combined_path: Optional[_Executor[Any]], template_path: _Executor[T]) -> None:
        """Initialize the joined terminal path.
        
        Args:
            combined_path: the combined path structure
            template_path: the template path that defines the execution behavior
        """
        super().__init__(combined_path)
        self._template_path = template_path
    
    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the joined path operation using the template path's logic.\n
        Delegates the actual execution logic to the template path's _apply method.
        
        Args:
            current: the current data element being processed
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from the template path's execution logic
        """
        yield from self._template_path._apply(current, remaining_path, contexts)


class _EnsureTypePath(_TerminalPath[T]):
    """Path element that ensures the current value is of a specific type.\n
    This path segment acts as a type filter, only continuing traversal if the current
    data element is an instance of the expected type. If the type check fails, no
    results are yielded.
    """
    def __init__(self, expected_type: Type[T], prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the type-checking path segment.
        
        Args:
            expected_type: the type that the current value must be an instance of
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.expected_type = expected_type
        
    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the type check to the current data.\n
        Checks if the current data element is an instance of the expected type and only
        continues traversal if the type check passes.
        
        Args:
            current: the current data element to type-check
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from continuing traversal if the type check passes
        """
        if isinstance(current, self.expected_type):
            yield from self._traverse(current, remaining_path, contexts)


class _YieldedKeyPlusValuePath(_TerminalPath[T]):
    """Path element that yields (key, value) pairs from dictionary iteration.\n
    This path segment iterates over dictionary items, applies a value path to each
    dictionary value, and yields tuples containing the key paired with each result
    from the value path traversal.
    """
    def __init__(self, value_path: _Executor[Any], prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the key-value pair path segment.
        
        Args:
            value_path: the path to apply to each dictionary value
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.value_path = value_path
        
    def _apply(self, current: Any, remaining_path: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply the key-value pair extraction to the current data.
        
        Iterates over dictionary items, applies the value path to each value, and yields
        tuples of (key, valueResult) for each result from the value path traversal.
        
        Args:
            current: the current data element (should be a dictionary)
            remaining_path: the remaining path segments to apply
            contexts: context information collected during traversal
            
        Yields:
            T: Results from continuing traversal with each (key, valueResult) tuple
        """
        if isinstance(current, dict):
            for key, value in current.items():
                value_results = list(self.value_path.walk(value))
                for result in value_results:
                    key_value_tuple = (key, result)
                    yield from self._traverse(key_value_tuple, remaining_path, contexts)


class _MultiValuePath(_TerminalPath[T]):
    """Path element that collects values from multiple sub-paths.\n
    This path segment applies multiple paths to the current data and yields all possible
    combinations of their results as tuples. Each path is evaluated independently, and
    the Cartesian product of all path results is generated.
    """
    def __init__(self, paths: tuple[_Executor[Any], ...], prev_path: Optional[_Executor[Any]] = None) -> None:
        """Initialize the multi-value path segment.
        
        Args:
            paths: a tuple of paths to apply to the current data
            prev_path: the previous path segment; defaults to None
        """
        super().__init__(prev_path)
        self.paths = paths
    
    def _apply(self, current: Any, _: list[_Executor[Any]], __: list[Any]) -> Generator[T, None, None]:
        """Apply multiple paths and yield all combinations of their results.
        
        Evaluates each path against the current data, collects all results, and yields
        every possible combination of results as tuples. If a path yields no results,
        None is used as a placeholder in the combinations.
        
        Args:
            current: the current data element to apply all paths to
            _: unused remaining path segments (terminal path)
            __: unused context information (terminal path)
            
        Yields:
            T: Each combination of results from all paths as a tuple
        """
        all_results = []
        for path in self.paths:
            path_results = list(path.walk(current))
            all_results.append(path_results if path_results else [None])
        
        for combination in itertools.product(*all_results):
            yield cast(T, combination)
