from .PathItem import PathItem

"""AddContext is a PathItem that represents adding the current value to the context"""
class AddContext(PathItem):
    def apply(self, current: str, context: list) -> tuple:
        """Apply the AddContext to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list
        
        Returns:
            tuple: the updated value and context list
        """
        return current, context + [current]