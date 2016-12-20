"""Node visitor"""
import ast

from .binopdesc import BinaryOperationDesc
from .cmpopdesc import CompareOperationDesc
from .nameconstdesc import NameConstantDesc
from .unaryopdesc import UnaryOperationDesc

from .context import Context
from .tokenendmode import TokenEndMode


class NodeVisitor(ast.NodeVisitor):
    """Node visitor"""
    def __init__(self, context=None):
        self.context = context if context is not None else Context()
        self.last_end_mode = TokenEndMode.LINE_FEED
        self.output = []

    def visit_Assign(self, node):
        """Visit assign"""
        target = self.visit_all(node.targets[0], inline=True)
        value = self.visit_all(node.value, inline=True)

        self.emit("local {target} = {value}".format(target=target, value=value))

    def visit_AugAssign(self, node):
        """Visit augassign"""
        operation = BinaryOperationDesc.OPERATION[node.op.__class__]

        target = self.visit_all(node.target, inline=True)

        values = {
            "left": target,
            "right": self.visit_all(node.value, inline=True),
            "operation": operation["value"],
        }

        line = "({})".format(operation["format"])
        line = line.format(**values)

        self.emit("{target} = {line}".format(target=target, line=line))

    def visit_Attribute(self, node):
        """Visit attribute"""
        line = "{object}.{attr}"
        values = {
            "object": self.visit_all(node.value, True),
            "attr": node.attr,
        }
        self.emit(line.format(**values))

    def visit_BinOp(self, node):
        """Visit binary operation"""
        operation = BinaryOperationDesc.OPERATION[node.op.__class__]
        line = "({})".format(operation["format"])
        values = {
            "left": self.visit_all(node.left, True),
            "right": self.visit_all(node.right, True),
            "operation": operation["value"],
        }

        self.emit(line.format(**values))

    def visit_Break(self, node):
        """Visit break"""
        self.emit("break")

    def visit_Call(self, node):
        """Visit function call"""
        line = "{name}({arguments})"

        name = self.visit_all(node.func, inline=True)
        arguments = [self.visit_all(arg, inline=True) for arg in node.args]

        self.emit(line.format(name=name, arguments=", ".join(arguments)))

    def visit_Compare(self, node):
        """Visit compare"""
        left = self.visit_all(node.left, inline=True)
        line = left
        for i, op_instance in enumerate(node.ops):
            right = node.comparators[i]
            operation = CompareOperationDesc.OPERATION[op_instance.__class__]
            right = self.visit_all(right, inline=True)
            line += " {op} {right}".format(op=operation, right=right)

        self.emit("({})".format(line))

    def visit_Delete(self, node):
        """Visit delete"""
        targets = [self.visit_all(target, inline=True) for target in node.targets]
        nils = ["nil" for _ in targets]
        line = "{targets} = {nils}".format(targets=", ".join(targets),
                                           nils=", ".join(nils))
        self.emit(line)

    def visit_Dict(self, node):
        """Visit dictionary"""
        keys = []

        for key in node.keys:
            value = self.visit_all(key, inline=True)
            if isinstance(key, ast.Str):
                value = "[{}]".format(value)
            keys.append(value)

        values = [self.visit_all(item, inline=True) for item in node.values]

        elements = ["{} = {}".format(keys[i], values[i]) for i in range(len(keys))]
        elements = ", ".join(elements)
        self.emit("dict {{{}}}".format(elements))

    def visit_Expr(self, node):
        """Visit expr"""
        output = self.visit_all(node.value)
        self.output.append(output)

    def visit_FunctionDef(self, node):
        """Visit function definition"""
        line = "local function {name}({arguments})"

        name = node.name
        arguments = [arg.arg for arg in node.args.args]

        function_def = line.format(name=name, arguments=", ".join(arguments))

        self.emit(function_def)
        self.visit_all(node.body)
        self.emit("end")

    def visit_For(self, node):
        """Visit for loop"""
        line = "for {target} in {iter} do"

        values = {
            "target": self.visit_all(node.target, inline=True),
            "iter": self.visit_all(node.iter, inline=True),
        }

        self.emit(line.format(**values))
        self.visit_all(node.body)
        self.emit("end")

    def visit_If(self, node):
        """Visit if"""
        test = self.visit_all(node.test, inline=True)

        line = "if {} then".format(test)

        self.emit(line)
        self.visit_all(node.body)

        if node.orelse:
            if isinstance(node.orelse[0], ast.If):
                elseif = node.orelse[0]
                elseif_test = self.visit_all(elseif.test, inline=True)

                line = "elseif {} then".format(elseif_test)
                self.emit(line)

                output_length = len(self.output)
                self.visit_If(node.orelse[0])

                del self.output[output_length]
                del self.output[-1]
            else:
                self.emit("else")
                self.visit_all(node.orelse)

        self.emit("end")

    def visit_IfExp(self, node):
        """Visit if expression"""
        line = "{cond} and {true_cond} or {false_cond}"
        values = {
            "cond": self.visit_all(node.test, inline=True),
            "true_cond": self.visit_all(node.body, inline=True),
            "false_cond": self.visit_all(node.orelse, inline=True),
        }

        self.emit(line.format(**values))

    def visit_Import(self, node):
        """Visit import"""
        line = 'local {asname} = require "{name}"'
        values = {"asname": "", "name": ""}

        if node.names[0].asname is None:
            values["name"] = node.names[0].name
            values["asname"] = values["name"]
            values["asname"] = values["asname"].split(".")[-1]
        else:
            values["asname"] = node.names[0].asname
            values["name"] = node.names[0].name

        self.emit(line.format(**values))

    def visit_Index(self, node):
        """Visit index"""
        self.emit(self.visit_all(node.value, inline=True))

    def visit_Lambda(self, node):
        """Visit lambda"""
        line = "function({arguments}) return"

        arguments = [arg.arg for arg in node.args.args]

        function_def = line.format(arguments=", ".join(arguments))

        output = []
        output.append(function_def)
        output.append(self.visit_all(node.body, inline=True))
        output.append("end")

        self.emit(" ".join(output))

    def visit_List(self, node):
        """Visit list"""
        elements = [self.visit_all(item, inline=True) for item in node.elts]
        line = "list {{{}}}".format(", ".join(elements))
        self.emit(line)

    def visit_Module(self, node):
        """Visit module"""
        self.visit_all(node.body)
        self.output = self.output[0]

    def visit_Name(self, node):
        """Visit name"""
        self.emit(node.id)

    def visit_NameConstant(self, node):
        """Visit name constant"""
        self.emit(NameConstantDesc.NAME[node.value])

    def visit_Num(self, node):
        """Visit number"""
        self.emit(str(node.n))

    def visit_Pass(self, node):
        """Visit pass"""
        pass

    def visit_Return(self, node):
        """Visit return"""
        line = "return "
        line += self.visit_all(node.value, inline=True)
        self.emit(line)

    def visit_Str(self, node):
        """Visit str"""
        self.emit('"{}"'.format(node.s))

    def visit_Subscript(self, node):
        """Visit subscript"""
        line = "{name}[{index}]"
        values = {
            "name": self.visit_all(node.value, inline=True),
            "index": self.visit_all(node.slice, inline=True),
        }

        self.emit(line.format(**values))

    def visit_Tuple(self, node):
        """Visit tuple"""
        elements = [self.visit_all(item, inline=True) for item in node.elts]
        self.emit(", ".join(elements))

    def visit_UnaryOp(self, node):
        """Visit unary operator"""
        operation = UnaryOperationDesc.OPERATION[node.op.__class__]
        value = self.visit_all(node.operand, inline=True)

        line = operation["format"]
        values = {
            "value": value,
            "operation": operation["value"],
        }

        self.emit(line.format(**values))

    def visit_While(self, node):
        """Visit while"""
        test = self.visit_all(node.test, inline=True)

        self.emit("while {} do".format(test))
        self.visit_all(node.body)
        self.emit("end")

    def generic_visit(self, node):
        """Unknown nodes handler"""
        raise RuntimeError("Unknown node: {}".format(node))

    def visit_all(self, nodes, inline=False):
        """Visit all nodes in the given list"""
        visitor = NodeVisitor(self.context)

        if isinstance(nodes, list):
            for node in nodes:
                visitor.visit(node)
            if not inline:
                self.output.append(visitor.output)
        else:
            visitor.visit(nodes)
            if not inline:
                self.output.extend(visitor.output)

        if inline:
            return " ".join(visitor.output)

    def emit(self, value):
        """Add translated value to the output"""
        self.output.append(value)
