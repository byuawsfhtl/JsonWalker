from .PathItem import PathItem
from .Index import Index
from .constants import MULTI_START, PATH_DIVIDER

"""MultiValue is a PathItem that represents multiple paths to take"""
class MultiValue(PathItem):
    def __init__(self, multiStr: str) -> None:
        """Create a new MultiValue object.

        Args:
            multiStr (str): a string of paths separated by MULTI_START
        """
        from JsonWalker.walk import pathParse
        assert MULTI_START in multiStr, f"MultiValue requires a {MULTI_START}-separated string"
        assert PATH_DIVIDER not in multiStr, "MultiValue cannot contain a path divider"
        self.multi = multiStr.split(MULTI_START)
        self.paths = [pathParse(mult) for mult in self.multi]
        for path in self.paths:
            for item in path:
                assert not isinstance(item, MultiValue), "MultiValue cannot contain another MultiValue"
                assert not isinstance(item, Index) or (item.start is not None and item.end is not None), "MultiValue cannot contain an Index without a specific index"

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
    