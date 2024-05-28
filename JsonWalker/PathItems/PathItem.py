"""PathItem is the base class for all path items"""
class PathItem:
    def apply(self, current, context):
        return current, context