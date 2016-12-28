"""Compare operation description"""
import ast


class CompareOperationDesc:
    """Compare operation description"""

    OPERATION = {
        ast.Eq: "==",
        ast.NotEq: "~=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.In: {
            "format": "operator_in({left}, {right})",
        },
        ast.NotIn: {
            "format": "not operator_in({left}, {right})",
        },
    }
