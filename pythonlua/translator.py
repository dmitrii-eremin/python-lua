"""Python to lua translator class"""
import ast
import os

from .config import Config
from .nodevisitor import NodeVisitor
from .astprinter import printAst
from .context import Context
class Translator:
    """Python to lua main class translator"""
    def __init__(self, config=None, show_ast=False, locals=None):
        self.config = config if config is not None else Config()
        self.context = Context(locals=locals)
        self.show_ast = show_ast

        self.output = []

    def translate(self, pycode):
        """Translate python code to lua code"""
        py_ast_tree = ast.parse(pycode)

        visitor = NodeVisitor(config=self.config,context=self.context)

        if self.show_ast:
            try: printAst(py_ast_tree)
            except: ast.dump(py_ast_tree)

        visitor.visit(py_ast_tree)

        self.output = visitor.output

        return self.to_code()

    def to_code(self, code=None, indent=0):
        """Create a lua code from the compiler output"""
        code = code if code is not None else self.output

        def add_indentation(line):
            """Add indentation to the given line"""
            indentation_width = 4
            indentation_space = " "

            indent_copy = max(indent, 0)

            return indentation_space * indentation_width * indent_copy + line

        lines = []
        for line in code:
            if isinstance(line, str):
                lines.append(add_indentation(line))
            elif isinstance(line, list):
                sub_code = self.to_code(line, indent + 1)
                lines.append(sub_code)

        return "\n".join(lines)

    @staticmethod
    def get_luainit(filename="luainit.lua"):
        """Get lua initialization code."""
        script_name = os.path.realpath(__file__)
        folder = os.path.dirname(script_name)
        luainit_path = os.path.join(folder, filename)

        with open(luainit_path) as file:
            return file.read()
        return ""
