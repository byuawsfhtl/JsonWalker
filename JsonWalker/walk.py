import itertools
from typing import (
    Generator, Any, Optional, Callable, TypeVar, Generic,
    Union, Type, cast, overload
)

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


class _Executor(Generic[T]):
    """Core path execution functionality - handles walking and traversing paths."""
    
    def __init__(self, prevPath: Optional['_Executor[Any]'] = None) -> None:
        self._prevPath = prevPath

    def walk(self, data: TypeForJsonLikeData) -> Generator[T, None, None]: # type: ignore
        """Execute the path query on the given JSON-like data."""
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _getFullPath(self) -> list['_Executor[Any]']:
        """Build the complete path by following the chain backwards."""
        path: list['_Executor[Any]'] = []
        current: Optional['_Executor[Any]'] = self
        while current:
            path.insert(0, current)
            current = current._prevPath
        return path

    def _traverse(self, current: Any, remainingPath: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Recursively traverse the data structure according to the path."""
        if current is None:
            return

        if not remainingPath:
            final_result = contexts + [current] if contexts else current
            yield cast(T, final_result)
            return

        pathItem = remainingPath[0]
        yield from pathItem._apply(current, remainingPath[1:], contexts.copy())

    def _apply(self, current: Any, remainingPath: list['_Executor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply this path item to the current data and continue traversal."""
        yield from self._traverse(current, remainingPath, contexts)


class _Builder:
    """Path building functionality - creates new path segments."""
    
    def key(self, keyName: str, default: Any = None) -> "KeyPath[Any]":
        """Creates a path segment that accesses a dictionary by a specific key."""
        return KeyPath(keyName, default, self)

    def listIndex(self, index: int) -> "IndexPath[Any]":
        """Creates a path segment that accesses a specific index in a list."""
        return IndexPath(index, self)

    def listSlice(self, start: Optional[int] = None, end: Optional[int] = None) -> "SlicePath[Any]":
        """Creates a path segment that accesses a range of elements in a list."""
        return SlicePath(start, end, self)

    def listAll(self) -> "SlicePath[Any]":
        """Creates a path segment that accesses all elements in a list."""
        return SlicePath(None, None, self)

    def yieldKey(self, valuePath: '_Executor[U]') -> "YieldedKeyPlusValuePath[tuple[str, U]]":
        """Creates a path that yields (key, value) pairs from dictionary iteration."""
        return YieldedKeyPlusValuePath(valuePath, self)

    def filter(self, conditionPath: '_Executor[Any]', condition: Callable[[Any], bool]) -> "FilteredPath[T]":
        """Creates a path segment that filters results based on a condition."""
        return FilteredPath(conditionPath, condition, self)

    def ensureType(self, expected_type: Type[U]) -> "EnsureTypePath[U]":
        """Creates a path segment that ensures the current value is of a specific type."""
        return EnsureTypePath(expected_type, self)

    # Multi method overloads
    @overload
    def multi(self, path1: '_Executor[U]') -> "MultiValuePath[tuple[U]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]') -> "MultiValuePath[tuple[U, V]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]') -> "MultiValuePath[tuple[U, V, W]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]') -> "MultiValuePath[tuple[U, V, W, X]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]') -> "_Executor[tuple[U, V, W, X, Y]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]', path8: '_Executor[A2]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]', path8: '_Executor[A2]', path9: '_Executor[A3]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]', path8: '_Executor[A2]', path9: '_Executor[A3]', path10: '_Executor[A4]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]', path8: '_Executor[A2]', path9: '_Executor[A3]', path10: '_Executor[A4]', path11: '_Executor[A5]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5]]": ...
    @overload
    def multi(self, path1: '_Executor[U]', path2: '_Executor[V]', path3: '_Executor[W]', path4: '_Executor[X]', path5: '_Executor[Y]', path6: '_Executor[Z]', path7: '_Executor[A1]', path8: '_Executor[A2]', path9: '_Executor[A3]', path10: '_Executor[A4]', path11: '_Executor[A5]', path12: '_Executor[A6]') -> "MultiValuePath[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5, A6]]": ...

    # Default for 13+ paths (no type hinting)
    def multi(self, *paths: 'JsonPath[Any]') -> "MultiValuePath[tuple[Any, ...]]":
        """Creates a path segment that collects multiple values from different sub-paths

        Args:
            *paths (JsonPath): one or more sub-paths to evaluate from the current point

        Returns:
            MultiValue: a JsonPath segment that gathers values from each of the provided paths
        """
        return MultiValuePath(paths, self)


class _TerminalPath(_Executor[T]):
    """Base class for path segments that cannot continue building (terminal)."""
    pass


class _ContinuablePath(_Executor[T], _Builder):
    """Base class for path segments that can continue building (non-terminal)."""
    @overload
    def add(self, path_to_add: "_TerminalPath[U]") -> "JoinedTerminalPath[U]": ...
    @overload
    def add(self, path_to_add: "_ContinuablePath[U]") -> "JoinedContinuablePath[U]": ...

    def add(self, path_to_add: "_Executor[U]") -> "_Executor[U]":
        """
        Combines the current path with another path segment, returning a new path.\n\n
        This method provides an object-oriented way to chain path objects together.The return type is inferred based on the path segment being added.
        If the added path is terminal (e.g., `multi()` or `yieldKey()`), the resulting path cannot be extended further, and your IDE will correctly reflect this.
        """
        is_terminal = isinstance(path_to_add, _TerminalPath)
        combined_path = self._combineTwoPaths(path_to_add)

        if is_terminal:
            return JoinedTerminalPath(combined_path, path_to_add)
        else:
            return JoinedContinuablePath(combined_path, path_to_add)

    def _combineTwoPaths(self, second: _Executor[Any]) -> Optional[_Executor[Any]]:
        """Combine two paths into a single chained path."""
        combinedPath = None
        # Clone segments of the first path into combined_path
        for segment in self._getFullPath():
            combinedPath = self._cloneSegment(segment, combinedPath)
        # Clone segments of the second path into combined_path
        for segment in second._getFullPath():
            combinedPath = self._cloneSegment(segment, combinedPath)
        return combinedPath
    
    @staticmethod
    def _cloneSegment(segment: _Executor[Any], prevPath: Optional[_Executor[Any]]) -> _Executor[Any]:
        """Create a copy of a path segment with a new previous path."""
        if isinstance(segment, KeyPath):
            return KeyPath(segment.dictKey, segment.default, prevPath)
        elif isinstance(segment, IndexPath):
            return IndexPath(segment.index, prevPath)
        elif isinstance(segment, SlicePath):
            return SlicePath(segment.start, segment.end, prevPath)
        elif isinstance(segment, YieldedKeyPlusValuePath):
            return YieldedKeyPlusValuePath(segment.valuePath, prevPath)
        elif isinstance(segment, MultiValuePath):
            return MultiValuePath(segment.paths, prevPath)
        elif isinstance(segment, FilteredPath):
            return FilteredPath(segment.conditionPath, segment.condition, prevPath)
        elif isinstance(segment, EnsureTypePath):
            return EnsureTypePath(segment.expectedType, prevPath)
        elif isinstance(segment, (JsonPath, _ContinuablePath, _TerminalPath, _Executor)):
            return _Executor(prevPath)
        else:
            raise TypeError(f"Unknown path segment type: {type(segment)}")


class JsonPath(_Executor[T], _Builder):
    """Main JsonPath class to start a path"""
    pass


# Non-terminal path segments (can continue building)
class KeyPath(_ContinuablePath[Any]):
    """Path element that accesses a dictionary key."""

    def __init__(self, key: str, default: Any = None, prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.dictKey = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, dict):
            value = current.get(self.dictKey, self.default)
            yield from self._traverse(value, remainingPath, contexts)


class IndexPath(_ContinuablePath[Any]):
    """Path element that accesses a list by index."""

    def __init__(self, index: int, prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, list) and -len(current) <= self.index < len(current):
            yield from self._traverse(current[self.index], remainingPath, contexts)


class SlicePath(_ContinuablePath[Any]):
    """Path element that accesses a slice of list items."""

    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, list):
            for item in current[self.start:self.end]:
                yield from self._traverse(item, remainingPath, contexts)


class FilteredPath(_ContinuablePath[T]):
    """Path element that filters the current value based on a condition."""
    
    def __init__(self, conditionPath: _Executor[Any], condition: Callable[[Any], bool], prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.conditionPath = conditionPath
        self.condition = condition
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        conditionResults = list(self.conditionPath.walk(current))
        if any(self.condition(res) for res in conditionResults):
            yield from self._traverse(current, remainingPath, contexts)


class JoinedContinuablePath(_ContinuablePath[T]):
    """A joined path that can continue building (when final path is non-terminal)."""
    
    def __init__(self, combined_path: Optional[_Executor[Any]], templatePath: _Executor[T]) -> None:
        super().__init__(combined_path)
        self._templatePath = templatePath
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        # Use the template path's _apply method for the actual logic
        yield from self._templatePath._apply(current, remainingPath, contexts)


# Terminal path segments (cannot continue building)
class JoinedTerminalPath(_TerminalPath[T]):
    """A joined path that cannot continue building (when final path is terminal)."""
    
    def __init__(self, combinedPath: Optional[_Executor[Any]], templatePath: _Executor[T]) -> None:
        super().__init__(combinedPath)
        self._templatePath = templatePath
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        """Use the template path's _apply method for the actual logic"""
        yield from self._templatePath._apply(current, remainingPath, contexts)


class EnsureTypePath(_TerminalPath[T]):
    """Path element that ensures the current value is of a specific type."""
    
    def __init__(self, expectedType: Type[T], prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.expectedType = expectedType
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        if isinstance(current, self.expectedType):
            yield from self._traverse(current, remainingPath, contexts)


class YieldedKeyPlusValuePath(_TerminalPath[T]):
    """Path element that yields (key, value) pairs from dictionary iteration."""
    
    def __init__(self, valuePath: _Executor[Any], prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.valuePath = valuePath
    
    def _apply(self, current: Any, remainingPath: list[_Executor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        if isinstance(current, dict):
            for key, value in current.items():
                value_results = list(self.valuePath.walk(value))
                for result in value_results:
                    keyValueTuple = (key, result)
                    yield from self._traverse(keyValueTuple, remainingPath, contexts)


class MultiValuePath(_TerminalPath[T]):
    """Path element that collects values from multiple sub-paths."""
    
    def __init__(self, paths: tuple[_Executor[Any], ...], prevPath: Optional[_Executor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.paths = paths
    
    def _apply(self, current: Any, _: list[_Executor[Any]], __: list[Any]) -> Generator[T, None, None]:
        allResults = []
        for path in self.paths:
            pathResults = list(path.walk(current))
            allResults.append(pathResults if pathResults else [None])
        
        for combination in itertools.product(*allResults):
            yield cast(T, combination)
