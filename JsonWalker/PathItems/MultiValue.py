from .PathItem import PathItem
from .Index import Index
from .constants import MULTI_START, PATH_DIVIDER

from JsonWalker.walk import pathParse

"""MultiValue is a PathItem that represents multiple paths to take"""
class MultiValue(PathItem):
    def __init__(self, multiStr: str):
        assert MULTI_START in multiStr, f"MultiValue requires a {MULTI_START}-separated string"
        assert PATH_DIVIDER not in multiStr, "MultiValue cannot contain a path divider"
        self.multi = multiStr.split(MULTI_START)
        self.paths = [pathParse(mult) for mult in self.multi]
        for path in self.paths:
            for item in path:
                assert not isinstance(item, MultiValue), "MultiValue cannot contain another MultiValue"
                assert not isinstance(item, Index) or (item.start is not None and item.end is not None), "MultiValue cannot contain an Index without a specific index"

    def apply(self, current, context):
        values = []
        for path in self.paths:
            new_current = current
            new_context = context
            for item in path:
                new_current, new_context = item.apply(new_current, new_context)
            values.append(new_current)
            context = new_context
        return values, context
    