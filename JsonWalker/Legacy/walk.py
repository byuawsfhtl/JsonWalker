from typing import Generator

from JsonWalker.Legacy.PathItems.DictIter import DictIter
from .PathItems.PathItem import PathItem
from .PathItems.Key import Key
from .PathItems.Index import Index
from .PathItems.Default import Default
from .PathItems.AddContext import AddContext
from .PathItems.MultiValue import MultiValue
from .PathItems.PathDivider import PathDivider
from .PathItems.Constants import CONTEXT_START, DICT_ITER_END, DICT_ITER_START, INDEX_START, INDEX_END, DEFAULT_START, DEFAULT_END, MULTI_START, MULTI_CONTINUE, PATH_DIVIDER

def pathParse(path: str) -> list[PathItem]:
    """Parses the path string into a list of PathItems

    Args:
        path (str): the path string to parse

    Returns:
        list: the list of PathItems
    """
    pathItems = []
    dividedPaths = path.split(PATH_DIVIDER)
    dividedPaths = [dividedPath.strip() for dividedPath in dividedPaths]
    counter = -1
    for currPath in dividedPaths:
        counter += 1
        while currPath:
            currPath = currPath.strip()
            index = 0
            if currPath[index] == CONTEXT_START:
                pathItems.append(AddContext())
                currPath = currPath[index+1:]
            elif currPath[index] == INDEX_START:
                indexOfClose = currPath.find(INDEX_END)
                pathItems.append(Index(currPath[index:indexOfClose+1]))
                currPath = currPath[indexOfClose+1:]
            elif currPath[index] == DEFAULT_START:
                indexOfClose = currPath.find(DEFAULT_END)
                pathItems.append(Default(currPath[index:indexOfClose+1]))
                currPath = currPath[indexOfClose+1:]
            elif MULTI_START in currPath:
                assert dividedPaths.index(currPath) == len(dividedPaths) - 1, "MultiValue must be the last path in the string"
                pathItems.append(MultiValue(currPath))
                break
            elif currPath[index] == PATH_DIVIDER or currPath[index] == MULTI_CONTINUE:
                pathItems.append(PathDivider())
                currPath = currPath[index+1:]
            elif currPath[index] == DICT_ITER_START:
                indexOfClose = currPath.find(DICT_ITER_END)
                pathItems.append(DictIter(currPath[index:indexOfClose+1]))
                currPath = currPath[indexOfClose+1:]
            else:
                endingIndex = len(currPath)
                for delimiter in [INDEX_START, DEFAULT_START, CONTEXT_START, MULTI_CONTINUE, PATH_DIVIDER, DICT_ITER_START]:
                    foundIndex = currPath.find(delimiter)
                    if foundIndex != -1 and foundIndex < endingIndex:
                        endingIndex = foundIndex
                pathItems.append(Key(currPath[index:endingIndex].strip()))
                currPath = currPath[endingIndex:]
        if counter < len(dividedPaths) - 1:
            pathItems.append(PathDivider())

    return pathItems

def walk(jsonData: dict | list, path: str | list[PathItem]) -> Generator[any, any, any]:
    """Get the nested value from the json data based on the path.

    Args:
        jsonData (dict | list): the json data to search through
        path (str | list[PathItem]): the path to the nested value

    Yields:
        Generator[any, any, any]: the contexts and the nested values requested
    """
    def navigate(current: any, path: list[PathItem], contexts: list) -> Generator[any, any, any]:
        """Navigate through the json data to find the nested value.

        Args:
            current (any): the current value in the json data that has been reached
            path (list[PathItem]): the remaining path to the nested value
            contexts (list): the contexts to raise with the nested value

        Yields:
            Generator[any, any, any]: the contexts and the nested values requested
        """
        if current is None:
            return
        if not path:
            if contexts:
                yield contexts + [current]
            else:
                yield current
        else:
            item = path[0]
            if isinstance(item, MultiValue):
                # MultiValue is a special case where it returns multiple values, so we yield each value
                values, newContext = item.apply(current, contexts)
                yield newContext + values
            elif isinstance(item, Index):
                # In order to iterate through a list, a range must be specified
                assert isinstance(current, list), f"Index can only be used on a list, not {current}"
                newCurrent, newContext = item.apply(current, contexts)
                if isinstance(newCurrent, list):
                    for value in newCurrent:
                        yield from navigate(value, path[1:], newContext)
                else:
                    yield from navigate(newCurrent, path[1:], newContext)
            elif isinstance(item, DictIter):
                assert isinstance(current, dict), f"DictIter can only be used on a dictionary, not {current}"
                newCurrent, newContext = item.apply(current, contexts)
                for key, value in newCurrent.items():
                    yield from navigate(value, path[1:], newContext + [key])
            else:
                newCurrent, newContext = item.apply(current, contexts)
                yield from navigate(newCurrent, path[1:], newContext)

    if isinstance(path, str):
        path = pathParse(path)
    yield from navigate(jsonData, path, [])