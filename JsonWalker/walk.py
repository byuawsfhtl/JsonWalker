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

class _PathExecutor(Generic[T]):
    """Core path execution functionality - handles walking and traversing paths."""
    
    def __init__(self, prevPath: Optional['_PathExecutor[Any]'] = None) -> None:
        self._prevPath = prevPath

    def _getFullPath(self) -> list['_PathExecutor[Any]']:
        """Build the complete path by following the chain backwards."""
        path: list['_PathExecutor[Any]'] = []
        current: Optional['_PathExecutor[Any]'] = self
        while current:
            path.insert(0, current)
            current = current._prevPath
        return path

    def walk(self, data: TypeForJsonLikeData) -> Generator[T, None, None]: # type: ignore
        """Execute the path query on the given JSON-like data."""
        pathItems = self._getFullPath()
        yield from self._traverse(data, pathItems, [])

    def _traverse(self, current: Any, remainingPath: list['_PathExecutor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Recursively traverse the data structure according to the path."""
        if current is None:
            return

        if not remainingPath:
            final_result = contexts + [current] if contexts else current
            yield cast(T, final_result)
            return

        pathItem = remainingPath[0]
        yield from pathItem._apply(current, remainingPath[1:], contexts.copy())

    def _apply(self, current: Any, remainingPath: list['_PathExecutor[Any]'], contexts: list[Any]) -> Generator[T, None, None]:
        """Apply this path item to the current data and continue traversal."""
        yield from self._traverse(current, remainingPath, contexts)


class _PathBuilder:
    """Path building functionality - creates new path segments."""
    
    def key(self, keyName: str, default: Any = None) -> "Key[Any]":
        """Creates a path segment that accesses a dictionary by a specific key."""
        return Key(keyName, default, self)

    def listIndex(self, idx: int) -> "Index[Any]":
        """Creates a path segment that accesses a specific index in a list."""
        return Index(idx, self)

    def listSlice(self, start: Optional[int] = None, end: Optional[int] = None) -> "Slice[Any]":
        """Creates a path segment that accesses a range of elements in a list."""
        return Slice(start, end, self)

    def listAll(self) -> "Slice[Any]":
        """Creates a path segment that accesses all elements in a list."""
        return Slice(None, None, self)

    def yieldKey(self, valuePath: '_PathExecutor[U]') -> "YieldedKeyAndValuePath[tuple[str, U]]":
        """Creates a path that yields (key, value) pairs from dictionary iteration."""
        return YieldedKeyAndValuePath(valuePath, self)

    def filter(self, conditionPath: '_PathExecutor[Any]', condition: Callable[[Any], bool]) -> "Filter[T]":
        """Creates a path segment that filters results based on a condition."""
        return Filter(conditionPath, condition, self)

    def ensureType(self, expected_type: Type[U]) -> "EnsureType[U]":
        """Creates a path segment that ensures the current value is of a specific type."""
        return EnsureType(expected_type, self)

    # Multi method overloads
    @overload
    def multi(self, path1: '_PathExecutor[U]') -> "MultiValue[tuple[U]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]') -> "MultiValue[tuple[U, V]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]') -> "MultiValue[tuple[U, V, W]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]') -> "MultiValue[tuple[U, V, W, X]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]') -> "_PathExecutor[tuple[U, V, W, X, Y]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]') -> "MultiValue[tuple[U, V, W, X, Y, Z]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]', path8: '_PathExecutor[A2]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]', path8: '_PathExecutor[A2]', path9: '_PathExecutor[A3]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]', path8: '_PathExecutor[A2]', path9: '_PathExecutor[A3]', path10: '_PathExecutor[A4]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]', path8: '_PathExecutor[A2]', path9: '_PathExecutor[A3]', path10: '_PathExecutor[A4]', path11: '_PathExecutor[A5]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5]]": ...
    @overload
    def multi(self, path1: '_PathExecutor[U]', path2: '_PathExecutor[V]', path3: '_PathExecutor[W]', path4: '_PathExecutor[X]', path5: '_PathExecutor[Y]', path6: '_PathExecutor[Z]', path7: '_PathExecutor[A1]', path8: '_PathExecutor[A2]', path9: '_PathExecutor[A3]', path10: '_PathExecutor[A4]', path11: '_PathExecutor[A5]', path12: '_PathExecutor[A6]') -> "MultiValue[tuple[U, V, W, X, Y, Z, A1, A2, A3, A4, A5, A6]]": ...

    # Default for 13+ paths (no type hinting)
    def multi(self, *paths: 'JsonPath[Any]') -> "MultiValue[tuple[Any, ...]]":
        """Creates a path segment that collects multiple values from different sub-paths

        Args:
            *paths (JsonPath): one or more sub-paths to evaluate from the current point

        Returns:
            MultiValue: a JsonPath segment that gathers values from each of the provided paths
        """
        return MultiValue(paths, self)

class JsonPath(_PathExecutor[T], _PathBuilder):
    """Main JsonPath class - combines execution and building capabilities."""
    pass


class _ContinuablePath(_PathExecutor[T], _PathBuilder):
    """Base class for path segments that can continue building (non-terminal)."""
    pass


class _TerminalPath(_PathExecutor[T]):
    """Base class for path segments that cannot continue building (terminal)."""
    pass


# Non-terminal path segments (can continue building)
class Key(_ContinuablePath[Any]):
    """Path element that accesses a dictionary key."""

    def __init__(self, key: str, default: Any = None, prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.dictKey = key
        self.default = default

    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, dict):
            value = current.get(self.dictKey, self.default)
            yield from self._traverse(value, remainingPath, contexts)


class Index(_ContinuablePath[Any]):
    """Path element that accesses a list by index."""

    def __init__(self, index: int, prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.index = index

    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, list) and -len(current) <= self.index < len(current):
            yield from self._traverse(current[self.index], remainingPath, contexts)


class Slice(_ContinuablePath[Any]):
    """Path element that accesses a slice of list items."""

    def __init__(self, start: Optional[int], end: Optional[int], prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.start = start
        self.end = end

    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[Any, None, None]:
        if isinstance(current, list):
            for item in current[self.start:self.end]:
                yield from self._traverse(item, remainingPath, contexts)


class Filter(_ContinuablePath[T]):
    """Path element that filters the current value based on a condition."""
    
    def __init__(self, conditionPath: _PathExecutor[Any], condition: Callable[[Any], bool], prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.conditionPath = conditionPath
        self.condition = condition
    
    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        conditionResults = list(self.conditionPath.walk(current))
        if any(self.condition(res) for res in conditionResults):
            yield from self._traverse(current, remainingPath, contexts)


class EnsureType(_ContinuablePath[T]):
    """Path element that ensures the current value is of a specific type."""
    
    def __init__(self, expected_type: Type[T], prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self.expected_type = expected_type
    
    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        if isinstance(current, self.expected_type):
            yield from self._traverse(current, remainingPath, contexts)


# Terminal path segments (cannot continue building)
class YieldedKeyAndValuePath(_TerminalPath[T]):
    """Path element that yields (key, value) pairs from dictionary iteration."""
    
    def __init__(self, valuePath: _PathExecutor[Any], prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self._valuePath = valuePath
    
    def _apply(self, current: Any, remainingPath: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        if isinstance(current, dict):
            for key, value in current.items():
                value_results = list(self._valuePath.walk(value))
                for result in value_results:
                    key_value_tuple = (key, result)
                    yield from self._traverse(key_value_tuple, remainingPath, contexts)


class MultiValue(_TerminalPath[T]):
    """Path element that collects values from multiple sub-paths."""
    
    def __init__(self, paths: tuple[_PathExecutor[Any], ...], prevPath: Optional[_PathExecutor[Any]] = None) -> None:
        super().__init__(prevPath)
        self._paths = paths
    
    def _apply(self, current: Any, _: list[_PathExecutor[Any]], __: list[Any]) -> Generator[T, None, None]:
        allResults = []
        for path in self._paths:
            path_results = list(path.walk(current))
            allResults.append(path_results if path_results else [None])
        
        for combination in itertools.product(*allResults):
            yield cast(T, combination)

class PathJoin: # TODO move to its own file and just export the join function, maybe rename to join path
    """Factory class for joining multiple paths together with proper type inference."""
    
    @overload
    @staticmethod
    def join(path1: _PathExecutor[T]) -> _PathExecutor[T]: ...
    
    @overload
    @staticmethod
    def join(path1: _PathExecutor[Any], path2: _PathExecutor[T]) -> _PathExecutor[T]: ...
    
    @overload
    @staticmethod
    def join(path1: _PathExecutor[Any], path2: _PathExecutor[Any], path3: _PathExecutor[T]) -> _PathExecutor[T]: ...
    
    @overload
    @staticmethod
    def join(path1: _PathExecutor[Any], path2: _PathExecutor[Any], path3: _PathExecutor[Any], path4: _PathExecutor[T]) -> _PathExecutor[T]: ...

    # TODO add more of these
    
    @staticmethod
    def join(*paths: _PathExecutor[Any]) -> _PathExecutor[Any]:
        """Join multiple paths together, preserving the type of the final path.
        
        Args:
            *paths: Variable number of paths to join in order
            
        Returns:
            _PathExecutor: A path that represents the combination of all input paths. The return type matches the final path's type (terminal vs continuable).
        """
        if not paths:
            raise ValueError("PathJoin requires at least one path")
        
        if len(paths) == 1:
            return paths[0]
        
        # Get the final path to determine if result should be terminal
        final_path = paths[-1]
        is_terminal = isinstance(final_path, _TerminalPath)
        
        # Build the combined path by chaining all segments
        combined_path = PathJoin._combine_paths(paths)
        
        # Return appropriate type based on final path
        if is_terminal:
            return JoinedTerminalPath(combined_path, final_path)
        else:
            return JoinedContinuablePath(combined_path, final_path)
    
    @staticmethod
    def _combine_paths(paths: tuple[_PathExecutor[Any], ...]) -> Optional[_PathExecutor[Any]]:
        """Combine multiple paths into a single chained path."""
        combined_path = None
        
        for path in paths:
            combined_path = PathJoin._append_path(combined_path, path)
        
        return combined_path
    
    @staticmethod
    def _append_path(current_path: Optional[_PathExecutor[Any]], path_to_append: _PathExecutor[Any]) -> Optional[_PathExecutor[Any]]:
        """Append one path to another by cloning all segments."""
        segments_to_append = path_to_append._getFullPath()
        
        for segment in segments_to_append:
            new_segment = PathJoin._clone_segment(segment, current_path)
            current_path = new_segment
        
        return current_path
    
    @staticmethod
    def _clone_segment(segment: _PathExecutor[Any], prev_path: Optional[_PathExecutor[Any]]) -> _PathExecutor[Any]:
        """Create a copy of a path segment with a new previous path."""
        if isinstance(segment, Key):
            return Key(segment.dictKey, segment.default, prev_path)
        elif isinstance(segment, Index):
            return Index(segment.index, prev_path)
        elif isinstance(segment, Slice):
            return Slice(segment.start, segment.end, prev_path)
        elif isinstance(segment, YieldedKeyAndValuePath):
            return YieldedKeyAndValuePath(segment.valuePath, prev_path)
        elif isinstance(segment, MultiValue):
            return MultiValue(segment._paths, prev_path)
        elif isinstance(segment, Filter):
            return Filter(segment.conditionPath, segment.condition, prev_path)
        elif isinstance(segment, EnsureType):
            return EnsureType(segment.expected_type, prev_path)
        elif isinstance(segment, (JsonPath, _ContinuablePath, _TerminalPath)):
            # For base path types, create a basic _PathExecutor
            return _PathExecutor(prev_path)
        else:
            raise TypeError(f"Unknown path segment type: {type(segment)}")


class JoinedContinuablePath(_ContinuablePath[T]):
    """A joined path that can continue building (when final path is non-terminal)."""
    
    def __init__(self, combined_path: Optional[_PathExecutor[Any]], template_path: _PathExecutor[T]) -> None:
        super().__init__(combined_path)
        self.template_path = template_path
    
    def _apply(self, current: Any, remaining_path: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        # Use the template path's _apply method for the actual logic
        yield from self.template_path._apply(current, remaining_path, contexts)


class JoinedTerminalPath(_TerminalPath[T]):
    """A joined path that cannot continue building (when final path is terminal)."""
    
    def __init__(self, combined_path: Optional[_PathExecutor[Any]], template_path: _PathExecutor[T]) -> None:
        super().__init__(combined_path)
        self.template_path = template_path
    
    def _apply(self, current: Any, remaining_path: list[_PathExecutor[Any]], contexts: list[Any]) -> Generator[T, None, None]:
        # Use the template path's _apply method for the actual logic
        yield from self.template_path._apply(current, remaining_path, contexts)