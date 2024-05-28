from .PathItem import PathItem

"""AddContext is a PathItem that represents adding the current value to the context"""
class AddContext(PathItem):
    def apply(self, current, context):
        return current, context + [current]