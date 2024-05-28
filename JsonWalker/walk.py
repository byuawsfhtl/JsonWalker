from .PathItems.PathItem import PathItem
from .PathItems.Key import Key
from .PathItems.Index import Index
from .PathItems.Default import Default
from .PathItems.AddContext import AddContext
from .PathItems.MultiValue import MultiValue
from .PathItems.PathDivider import PathDivider
from .PathItems.constants import CONTEXT_START, INDEX_START, INDEX_END, DEFAULT_START, DEFAULT_END, MULTI_START, MULTI_CONTINUE, PATH_DIVIDER

def pathParse(path: str) -> list[PathItem]:
    """Parses the path string into a list of PathItems

    Args:
        path (str): the path string to parse

    Returns:
        list: the list of PathItems
    """
    path_items = []
    dividedPaths = path.split(PATH_DIVIDER)
    dividedPaths = [dividedPath.strip() for dividedPath in dividedPaths]
    counter = -1
    for curr_path in dividedPaths:
        counter += 1
        while curr_path:
            curr_path = curr_path.strip()
            index = 0
            if curr_path[index] == CONTEXT_START:
                path_items.append(AddContext())
                curr_path = curr_path[index+1:]
            elif curr_path[index] == INDEX_START:
                indexOfClose = curr_path.find(INDEX_END)
                path_items.append(Index(curr_path[index:indexOfClose+1]))
                curr_path = curr_path[indexOfClose+1:]
            elif curr_path[index] == DEFAULT_START:
                indexOfClose = curr_path.find(DEFAULT_END)
                path_items.append(Default(curr_path[index:indexOfClose+1]))
                curr_path = curr_path[indexOfClose+1:]
            elif MULTI_START in curr_path:
                assert dividedPaths.index(curr_path) == len(dividedPaths) - 1, "MultiValue must be the last path in the string"
                path_items.append(MultiValue(curr_path))
                break
            elif curr_path[index] == PATH_DIVIDER or curr_path[index] == MULTI_CONTINUE:
                path_items.append(PathDivider())
                curr_path = curr_path[index+1:]
            else:
                endingIndex = len(curr_path)
                for delimiter in [INDEX_START, DEFAULT_START, CONTEXT_START, MULTI_CONTINUE, PATH_DIVIDER]:
                    foundIndex = curr_path.find(delimiter)
                    if foundIndex != -1 and foundIndex < endingIndex:
                        endingIndex = foundIndex
                path_items.append(Key(curr_path[index:endingIndex].strip()))
                curr_path = curr_path[endingIndex:]
        if counter < len(dividedPaths) - 1:
            path_items.append(PathDivider())

    return path_items

def walk(jsonData: dict | list, path: str | list[PathItem]):
    """Get the nested value from the json data based on the path.

    Args:
        jsonData (dict | list): the json data to search through
        path (str | list[PathItem]): the path to the nested value

    Yields:
        tuple: the contexts and the nested values requested
    """
    def navigate(current: any, path: list[PathItem], contexts: list):
        """Navigate through the json data to find the nested value.

        Args:
            current (any): the current value in the json data that has been reached
            path (list[PathItem]): the remaining path to the nested value
            contexts (list): the contexts to raise with the nested value

        Yields:
            tuple: the contexts and the nested values requested
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
                values, new_context = item.apply(current, contexts)
                yield new_context + values
            elif isinstance(item, Index):
                # In order to iterate through a list, a range must be specified
                assert isinstance(current, list), "Index can only be used on a list"
                new_current, new_context = item.apply(current, contexts)
                if isinstance(new_current, list):
                    for value in new_current:
                        yield from navigate(value, path[1:], new_context)
                else:
                    yield from navigate(new_current, path[1:], new_context)
            else:
                new_current, new_context = item.apply(current, contexts)
                yield from navigate(new_current, path[1:], new_context)

    if isinstance(path, str):
        path = pathParse(path)
    yield from navigate(jsonData, path, [])