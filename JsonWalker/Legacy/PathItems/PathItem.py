"""PathItem is the base class for all path items"""
class PathItem:
    def apply(self, current: str, context: list) -> tuple:
        """Apply the PathItem to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the updated value and context list
        """
        return current, context