"""Node visitor"""
import ast

from .binopdesc import BinaryOperationDesc
from .boolopdesc import BooleanOperationDesc
from .cmpopdesc import CompareOperationDesc
from .nameconstdesc import NameConstantDesc
from .unaryopdesc import UnaryOperationDesc

from .context import Context
from .loopcounter import LoopCounter
from .tokenendmode import TokenEndMode
import re
class NodeVisitor(ast.NodeVisitor):
    LUACODE = r"^\[\[luacode(=.+)?\]\].*"

    """Node visitor"""
    def __init__(self, context=None, config=None):
        self.context = context if context is not None else Context()
        self.config = config
        self.last_end_mode = TokenEndMode.LINE_FEED
        self.output = []

    def visit_Assign(self, node):
        """Visit assign"""
        target = self.visit_all(node.targets[0], inline=True)
        value = self.visit_all(node.value, inline=True)
        target_name = target
        if "[" in target_name:
            target_name = target_name[:target_name.index("[")]

        local_keyword = ""

        last_ctx = self.context.last()

        if last_ctx["class_name"]:
            target = ".".join([last_ctx["class_name"], target])
        if not (self.context.top() and not self.config["top_locals"]) and "." not in target and not last_ctx["locals"].exists(target_name) and not last_ctx["globals"].exists(target_name):
            local_keyword = "local "
        if "." not in target and not last_ctx["locals"].exists(target_name) and not last_ctx["globals"].exists(target_name):
            last_ctx["locals"].add_symbol(target)


        self.emit("{local}{target} = {value}".format(local=local_keyword,
                                                     target=target,
                                                     value=value))

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

    def visit_Assert(self,node):
        line = "assert({})"
        self.emit(line.format(self.visit_all(node.test, True)))

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

    def visit_BoolOp(self, node):
        """Visit boolean operation"""
        operation = BooleanOperationDesc.OPERATION[node.op.__class__]
        # changed this for cases where multiple boolops are linked (e.g.: a and b and c)
        line = "({})".format(operation.join([self.visit_all(v,True) for v in node.values]))
        self.emit(line)

    def visit_Break(self, node):
        """Visit break"""
        self.emit("break")

    def visit_Bytes(self, node):
        self.emit(str(int.from_bytes(node.s, byteorder='big')))

    def visit_Call(self, node):
        """Visit function call"""
        line = "{name}({arguments})"
        if 'attr' in node.func.__dict__:
            name = self.visit_all(node.func, inline=True)
            spl = name.rsplit(".",1)
            last_ctx = self.context.last()
            if not "static_identifier" in last_ctx: last_ctx["static_identifier"] = ""
            if spl[0] not in ["math","os","coroutine","table","string",self.context.last()['static_identifier']]:
                name = ":".join(spl)
        else:
            name = self.visit_all(node.func, inline=True)
        arguments = [self.visit_all(arg, inline=True) for arg in node.args]
        self.emit(line.format(name=name, arguments=", ".join(arguments)))

    def visit_ClassDef(self, node):
        """Visit class definition"""
        bases = [self.visit_all(base, inline=True) for base in node.bases]

        local_keyword = ""
        last_ctx = self.context.last()
        if not (self.context.top() and not self.config["top_locals"]) and not last_ctx["class_name"] and not last_ctx["locals"].exists(node.name) and not last_ctx["globals"].exists(node.name):
            local_keyword = "local "
        if not last_ctx["class_name"] and not last_ctx["locals"].exists(node.name) and not last_ctx["globals"].exists(node.name):
            last_ctx["locals"].add_symbol(node.name)

        name = node.name
        if last_ctx["class_name"]:
            name = ".".join([last_ctx["class_name"], name])

        # create metatable methods for operator overloading
        mtmethods = {}
        properties = {}
        for nnode in node.body:
            if type(nnode) == ast.FunctionDef:
                try: dl = [decorator.id for decorator in reversed(nnode.decorator_list)]
                except: pass
                if "property" in dl:
                    properties[nnode.name] = '\"{}\"'.format(".".join([name, nnode.name]))
                if nnode.name in ["__add__","__sub__",
                                  "__eq__","__ne__",
                                  "__lt__","__le__","__gt__","__ge__",
                                  "__mul__","__div__",
                                  "__mod__","__pow__",
                                  "__len__",
                                  "__gc__"]:  # the GC module does not work in python, but it does in lua!
                    mtmethods[nnode.name.rstrip("_")] = "\"{}\"".format(nnode.name)
                if nnode.name == "__truediv__":  # different since python 3
                    mtmethods["__div"] = "\"{}\"".format(nnode.name)
                if nnode.name == "__str__":
                    mtmethods["__tostring"] = "\"{}\"".format(nnode.name)
                if nnode.name == "__contains__":
                    mtmethods["__in"] = "\"{}\"".format(nnode.name)

        mtmethods = ", ".join(["{} = {}".format(key,mtmethods[key]) for key in mtmethods])
        properties = ", ".join(["{} = {}".format(key,properties[key]) for key in properties])
        values = {
            "local": local_keyword,
            "name": name,
            "node_name": node.name,
            "mtmethods": mtmethods
        }

        self.emit("{local}{name} = class(function({node_name})".format(**values))
        self.context.push({"class_name": node.name})
        self.visit_all(node.body)
        self.context.pop()

        self.output[-1].append("return {node_name}".format(**values))

        self.emit("end, \"{}\", {{{}}}, {{{}}}, {{{}}})".format(node.name, ", ".join(bases),mtmethods,properties))

        # Return class object only in the top-level classes.
        # Not in the nested classes.
        if self.config["class"]["return_at_the_end"] and not last_ctx["class_name"]:
            self.emit("return {}".format(name))

    def visit_Compare(self, node):
        """Visit compare"""

        line = ""
        left = self.visit_all(node.left, inline=True)
        for i in range(len(node.ops)):
            operation = node.ops[i]

            operation = CompareOperationDesc.OPERATION[operation.__class__]

            right = self.visit_all(node.comparators[i], inline=True)

            values = {
                "left": left,
                "right": right,
            }

            if isinstance(operation, str):
                values["op"] = operation
                line += "{left} {op} {right}".format(**values)
            elif isinstance(operation, dict):
                line += operation["format"].format(**values)

            if i < len(node.ops) - 1:
                left = right
                line += " and "

        self.emit("({})".format(line))

    def visit_Continue(self, node):
        """Visit continue"""
        last_ctx = self.context.last()
        line = "goto {}".format(last_ctx["loop_label_name"])
        self.emit(line)

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
            if isinstance(key, ast.Str) or isinstance(key, ast.Name):
                value = "[{}]".format(value)
            keys.append(value)

        values = [self.visit_all(item, inline=True) for item in node.values]

        elements = ["{} = {}".format(keys[i], values[i]) for i in range(len(keys))]
        elements = ", ".join(elements)
        self.emit("dict {{{}}}".format(elements))

    def visit_DictComp(self, node):
        """Visit dictionary comprehension"""
        self.emit("(function()")
        self.emit("local result = dict {}")

        ends_count = 0

        for comp in node.generators:
            line = "for {target} in {iterator} do"
            values = {
                "target": self.visit_all(comp.target, inline=True),
                "iterator": self.visit_all(comp.iter, inline=True),
            }
            line = line.format(**values)
            self.emit(line)
            ends_count += 1

            for if_ in comp.ifs:
                line = "if {} then".format(self.visit_all(if_, inline=True))
                self.emit(line)
                ends_count += 1

        line = "result[{key}] = {value}"
        values = {
            "key": self.visit_all(node.key, inline=True),
            "value": self.visit_all(node.value, inline=True),
        }
        self.emit(line.format(**values))

        self.emit(" ".join(["end"] * ends_count))

        self.emit("return result")
        self.emit("end)()")

    def visit_Ellipsis(self, node):
        """Visit ellipsis"""
        self.emit("...")

    def visit_Expr(self, node):
        """Visit expr"""
        expr_is_docstring = False
        if isinstance(node.value, ast.Str):
            expr_is_docstring = True

        self.context.push({"docstring": expr_is_docstring})
        output = self.visit_all(node.value)
        self.context.pop()

        self.output.append(output)

    def visit_FunctionDef(self, node):
        """Visit function definition"""

        last_ctx = self.context.last()
        # check for decorators and implement them directly on the function.
        # This is required for python decorator properties to work.
        line = 'function({arguments})'
        end = 'end'
        decorator_name = ''
        for decorator in reversed(node.decorator_list):
            decorator_name = self.visit_all(decorator, inline=True)
            # make sure that it uses methods instead of global functions when they are available
            if last_ctx["methods"].exists(decorator_name.split(".")[0]) and last_ctx["class_name"]:
                decorator_name = ":".join(decorator_name.rsplit(".",1))
                decorator_name = ".".join([last_ctx["class_name"],decorator_name])
            # add the decorator to the function definition.
            line = '{}({}'.format(decorator_name,line)
            end = '{})'.format(end)

        if decorator_name:
            line = "{local}{name} = "+line
        else:
            # if there is no decorator then we can define the function normally
            line = "{local}function {name}({arguments})"


        name = node.name
        if last_ctx["class_name"]:
            last_ctx["methods"].add_symbol(name)
            name = ".".join([last_ctx["class_name"], name])

        arguments = [arg.arg for arg in node.args.args]

        if node.args.vararg is not None:
            arguments.append("...")

        local_keyword = ""

        # added the top function for the context, since we want things in the topmost layer to be defined globally
        # I should probably add something in config for it but at the moment I am too lazy.
        if not (self.context.top() and not self.config["top_locals"]) and "." not in name and not last_ctx["locals"].exists(name) and not last_ctx["globals"].exists(name):
            local_keyword = "local "
        if "." not in name and not last_ctx["locals"].exists(name) and not last_ctx["globals"].exists(name):
            last_ctx["locals"].add_symbol(name)

        function_def = line.format(local=local_keyword,
                                   name=name,
                                   arguments=", ".join(arguments))

        self.emit(function_def)

        self.context.push({"class_name": "", "static_identifier": last_ctx['class_name']})
        # append function arguments as local vars
        for arg in node.args.args:
            self.context.last()["locals"].add_symbol(arg.arg)
        self.visit_all(node.body)
        self.context.pop()

        body = self.output[-1]

        if node.args.vararg is not None:
            line = "local {name} = list {{...}}".format(name=node.args.vararg.arg)
            body.insert(0, line)

        arg_index = -1
        for i in reversed(node.args.defaults):
            line = "{name} = {name} or {value}"

            arg = node.args.args[arg_index]
            values = {
                "name": arg.arg,
                "value": self.visit_all(i, inline=True),
            }
            body.insert(0, line.format(**values))

            arg_index -= 1

        # the end variable also closes parameters for possible decorators.
        self.emit(end)


    def visit_For(self, node):
        """Visit for loop"""
        line = "for {target} in {iter} do"

        values = {
            "target": self.visit_all(node.target, inline=True),
            "iter": self.visit_all(node.iter, inline=True),
        }

        self.emit(line.format(**values))

        continue_label = LoopCounter.get_next()
        self.context.push({
            "loop_label_name": continue_label,
        })
        self.visit_all(node.body)
        self.context.pop()

        self.output[-1].append("::{}::".format(continue_label))

        self.emit("end")

    def visit_Global(self, node):
        """Visit globals"""
        last_ctx = self.context.last()
        for name in node.names:
            last_ctx["globals"].add_symbol(name)

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
        line = 'local {asname} = require("{name}")'
        values = {"asname": "", "name": ""}

        if node.names[0].asname is None:
            values["name"] = node.names[0].name
            values["asname"] = values["name"]
            values["asname"] = values["asname"].split(".")[-1]
        else:
            values["asname"] = node.names[0].asname
            values["name"] = node.names[0].name

        self.emit(line.format(**values))

    def visit_ImportFrom(self, node):
        """Visit import"""
        line = 'require("{module}")'
        values = {"module": node.module }
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

    def visit_ListComp(self, node):
        """Visit list comprehension"""
        self.emit("(function()")
        self.emit("local result = list {}")

        ends_count = 0

        for comp in node.generators:
            line = "for {target} in {iterator} do"
            values = {
                "target": self.visit_all(comp.target, inline=True),
                "iterator": self.visit_all(comp.iter, inline=True),
            }
            line = line.format(**values)
            self.emit(line)
            ends_count += 1

            for if_ in comp.ifs:
                line = "if {} then".format(self.visit_all(if_, inline=True))
                self.emit(line)
                ends_count += 1

        line = "result:append({})"
        line = line.format(self.visit_all(node.elt, inline=True))
        self.emit(line)

        self.emit(" ".join(["end"] * ends_count))

        self.emit("return result")
        self.emit("end)()")

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


    def visit_Slice(self,node):
        values = {
            'lower': self.visit_all(node.lower,inline=True) if node.lower else "nil",
            'upper': self.visit_all(node.upper,inline=True) if node.upper else "nil",
            'step': self.visit_all(node.step,inline=True)  if node.step else "nil"
        }
        self.emit("Slice({lower},{upper},{step})".format(**values))

    def visit_Starred(self, node):
        """Visit starred object"""
        value = self.visit_all(node.value, inline=True)
        line = "unpack({})".format(value)
        self.emit(line)

    def visit_Str(self, node):
        """Visit str"""
        value = node.s
        m = re.match(NodeVisitor.LUACODE, value)
        if m:
            value = value[m.end():]
            if m.groups()[0]:
                fn = m.groups()[0][1:]
                try:
                    import os
                    with open(fn,'r') as f:
                        lns = f.readlines()
                    value = "".join(lns) + "\n" + value
                except:
                    print('Warning: LUA file ({}) not found'.format(os.path.join(os.getcwd(),fn)))
            self.emit(value)
        elif self.context.last()["docstring"]:
            self.emit('--[[ {} ]]'.format(node.s))
        else:
            if '\n' in node.s:
                self.emit('([[{}]])'.format(node.s))
            else:
                self.emit('("{}")'.format(node.s))

    def visit_Subscript(self, node):
        """Visit subscript"""
        line = "{name}[{index}]"
        values = {
            "name": self.visit_all(node.value, inline=True),
            "index": self.visit_all(node.slice, inline=True),
        }

        self.emit(line.format(**values))

    def visit_Try(self,node):
        """Visit try"""
        self.emit("xpcall(function()")
        self.visit_all(node.body)
        self.emit('end, function(Error)')
        for handler in node.handlers:
            self.visit_all(handler.body)
        self.emit('end)')

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

        continue_label = LoopCounter.get_next()
        self.context.push({
            "loop_label_name": continue_label,
        })
        self.visit_all(node.body)
        self.context.pop()

        self.output[-1].append("::{}::".format(continue_label))

        self.emit("end")

    def visit_With(self, node):
        """Visit with"""
        self.emit("do")

        self.visit_all(node.body)

        body = self.output[-1]
        lines = []
        for i in node.items:
            line = ""
            if i.optional_vars is not None:
                line = "local {} = "
                line = line.format(self.visit_all(i.optional_vars,
                                                  inline=True))
            line += self.visit_all(i.context_expr, inline=True)
            lines.append(line)

        for line in lines:
            body.insert(0, line)

        self.emit("end")

    def generic_visit(self, node):
        """Unknown nodes handler"""
        raise RuntimeError("Unknown node: {}".format(node))

    def visit_all(self, nodes, inline=False):
        """Visit all nodes in the given list"""

        if not inline:
            last_ctx = self.context.last()
            last_ctx["locals"].push()

        visitor = NodeVisitor(context=self.context, config=self.config)

        if isinstance(nodes, list):
            for node in nodes:
                visitor.visit(node)
            if not inline:
                self.output.append(visitor.output)
        else:
            visitor.visit(nodes)
            if not inline:
                self.output.extend(visitor.output)

        if not inline:
            last_ctx = self.context.last()
            last_ctx["locals"].pop()

        if inline:
            return " ".join(visitor.output)

    def emit(self, value):
        """Add translated value to the output"""
        self.output.append(value)
