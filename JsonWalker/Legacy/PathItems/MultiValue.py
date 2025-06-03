from JsonWalker.Legacy.PathItems.DictIter import DictIter
from .PathItem import PathItem
from .Index import Index
from .Constants import MULTI_START, PATH_DIVIDER

"""MultiValue is a PathItem that represents multiple paths to take"""
class MultiValue(PathItem):
    def __init__(self, multiStr: str) -> None:
        """Create a new MultiValue object.

        Args:
            multiStr (str): a string of paths separated by MULTI_START
        """
        from JsonWalker.Legacy.walk import pathParse
        self.multi = self._stripMulti(multiStr)
        self.paths = [pathParse(mult) for mult in self.multi]
        for path in self.paths:
            for item in path:
                self._innerPathRules(item)

    def _stripMulti(self, check: str) -> list[str]:
        """Break the multi string into the individual paths.

        Args:
            check (str): the multi string to break

        Returns:
            list[str]: the broken up multi string
        """
        assert MULTI_START in check, f"MultiValue requires a {MULTI_START}-separated string"
        assert PATH_DIVIDER not in check, "MultiValue cannot contain a path divider"
        return check.split(MULTI_START)
    
    def _innerPathRules(self, item: PathItem) -> None:
        """Apply the inner path rules to the item.

        Args:
            item (PathItem): the PathItem to check
        """
        assert not isinstance(item, MultiValue), "MultiValue cannot contain another MultiValue"
        assert not isinstance(item, Index) or (item.start is not None and item.end is not None), "MultiValue cannot contain an Index specification without a specific index"
        assert not isinstance(item, DictIter), "MultiValue cannot contain a DictIter"

    def apply(self, current: str, context: list) -> tuple:
        """Apply the MultiValue to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the list of values and the updated context list
        """
        values = []
        for path in self.paths:
            newCurrent = current
            newContext = context
            for item in path:
                newCurrent, newContext = item.apply(newCurrent, newContext)
            values.append(newCurrent)
            context = newContext
        return values, context
    