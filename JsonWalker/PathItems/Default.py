import ast
from .PathItem import PathItem
from .constants import DEFAULT_START, DEFAULT_END, DEFAULT_TYPE_DELIMITER

"""Default is a PathItem that represents a default value to use if the current value is None."""
class Default(PathItem):
    def __init__(self, defaultStr: str):
        assert defaultStr.startswith(DEFAULT_START) and defaultStr.endswith(DEFAULT_END), f"Default must be in the form {DEFAULT_START}value{DEFAULT_TYPE_DELIMITER}type{DEFAULT_END}"
        assert DEFAULT_TYPE_DELIMITER in defaultStr, f"Default must have a type"
        defaultStr = defaultStr[1:-1]
        default, default_type = defaultStr.split(DEFAULT_TYPE_DELIMITER)
        self.default = castValue(default.strip(), default_type.strip())

    def apply(self, current, context):
        if current is None:
            return self.default, context
        return current, context
    
def castValue(value, valueType):
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