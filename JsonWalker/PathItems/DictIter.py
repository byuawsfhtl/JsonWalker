from .PathItem import PathItem
from .Constants import DICT_ITER_START, DICT_ITER_END

class DictIter(PathItem):
    def __init__(self, dictStr: str) -> None:
        """Create a new DictIter object.

        Args:
            dictStr (str): the path string to specify the dictionary iteration
        """
        assert dictStr.startswith(DICT_ITER_START) and dictStr.endswith(DICT_ITER_END), f"DictIter must be in the form {DICT_ITER_START}*{DICT_ITER_END}"
        self.dictStr = dictStr[1:-1]

        assert self.dictStr == "*", "DictIter must be in the form {DICT_ITER_START}*{DICT_ITER_END}"

    def apply(self, current: dict, context: list) -> tuple[dict, list]:
        """Apply the PathItem to the current value and context.

        Args:
            current (dict): the current value
            context (list): the current context list

        Returns:
            tuple: the updated value and context list
        """
        return current, context