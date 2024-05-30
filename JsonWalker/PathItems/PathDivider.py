"""PathDivider is a PathItem that represents divisions in path parts"""
from .PathItem import PathItem

class PathDivider(PathItem):
    def apply(self, current: str, context: list) -> tuple:
        """Apply the PathDivider to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list
        
        Returns:   
            tuple: the updated value and context list
        """
        return current, context