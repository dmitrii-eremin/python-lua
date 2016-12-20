"""Boolean operation description"""
import ast


_DEFAULT_FORMAT = "{left} {operation} {right}"


class BooleanOperationDesc:
    """Binary operation description"""

    OPERATION = {
        ast.And: {
            "value": "and",
            "format": _DEFAULT_FORMAT,
        },
        ast.Or: {
            "value": "or",
            "format": _DEFAULT_FORMAT,
        },
    }
