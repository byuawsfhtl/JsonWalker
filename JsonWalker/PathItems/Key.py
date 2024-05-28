from .PathItem import PathItem

"""Key is a PathItem that represents a key in a dictionary"""
class Key(PathItem):
    def __init__(self, key: str):
        self.key = key

    def apply(self, current, context):
        if isinstance(current, dict):
            return current.get(self.key, None), context
        return current, context