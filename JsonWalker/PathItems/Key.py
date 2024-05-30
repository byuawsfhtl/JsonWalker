from .PathItem import PathItem

"""Key is a PathItem that represents a key in a dictionary"""
class Key(PathItem):
    def __init__(self, key: str) -> None:
        """Create a new Key object.

        Args:
            key (str): the key to look for
        """
        self.key = key

    def apply(self, current: str, context: list) -> tuple:
        """Apply the Key to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the value at the key and the updated context list
        """
        if isinstance(current, dict):
            return current.get(self.key, None), context
        return current, context