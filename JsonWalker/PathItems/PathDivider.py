"""PathDivider is a PathItem that represents divisions in path parts"""
from .PathItem import PathItem

class PathDivider(PathItem):
    def apply(self, current, context):
        return current, context