import ast
from .PathItem import PathItem
from .Constants import DEFAULT_START, DEFAULT_END, DEFAULT_TYPE_DELIMITER

"""Default is a PathItem that represents a default value to use if the current value is None."""
class Default(PathItem):
    def __init__(self, defaultStr: str) -> None:
        """Create a new Default object.

        Args:
            defaultStr (str): a string of the default value and type
        """
        defaultStr = self._stripDefault(defaultStr)
        default, defaultType = defaultStr.split(DEFAULT_TYPE_DELIMITER)
        self.default = self.castValue(default.strip(), defaultType.strip())

    def _stripDefault(self, check: str) -> str:
        """Strip the default string of the default delimiters.

        Args:
            check (str): the default string to strip

        Returns:
            str: the stripped default string
        """
        assert check.startswith(DEFAULT_START) and check.endswith(DEFAULT_END), f"Default must be in the form {DEFAULT_START}value{DEFAULT_TYPE_DELIMITER}type{DEFAULT_END}"
        assert DEFAULT_TYPE_DELIMITER in check, f"Default must have a type"
        return check[1:-1]

    def apply(self, current: str, context: list) -> tuple:
        """Apply the Default to the current value and context.

        Args:
            current (str): the current value
            context (list): the current context list

        Returns:
            tuple: the updated value and context list
        """
        if current is None:
            return self.default, context
        return current, context
    
    def castValue(self, value: str, valueType: str) -> any:
        """Casts the value to the specified type

        Args:
            value (str): the value to cast
            valueType (str, optional): the type to cast to; defaults to None

        Raises:
            ValueError: if the valueType is invalid

        Returns:
            any: the value cast to the specified type
        """
        if '\'' in value or '\"' in value:
            value = value.strip('\'').strip('\"')
        
        convertDict = {
            'int': int,
            'str': str,
            'float': float,
            'bool': lambda x: x.lower() in ('true', '1'),
            'list': ast.literal_eval,
            'dict': ast.literal_eval
        }
        
        if valueType not in convertDict.keys():
            raise ValueError(f"Invalid type: {valueType}")
        
        try:
            return convertDict[valueType](value)
        except ValueError:
            return value