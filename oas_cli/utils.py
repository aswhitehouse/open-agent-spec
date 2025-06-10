PY_TYPE_MAP = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool",
}

def map_yaml_type(yaml_type: str) -> str:
    """Return the Python type hint for a YAML type string."""
    return PY_TYPE_MAP.get(yaml_type.lower(), "str")
