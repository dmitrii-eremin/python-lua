"""Class to store the python code context"""
from .symbolsstack import SymbolsStack
from .tokenendmode import TokenEndMode


class Context:
    """Class to store the python code context"""
    def __init__(self, values=None):
        values = values if values is not None else {
            "token_end_mode": TokenEndMode.LINE_FEED,
            "class_name": "",
            "locals": SymbolsStack(),
            "globals": SymbolsStack(),  # Not working yet
            "loop_label_name": "",
            "docstring": False,
        }

        self.ctx_stack = [values]

    def last(self):
        """Return actual context state"""
        return self.ctx_stack[-1]

    def push(self, values):
        """Push new context state with new values"""
        value = self.ctx_stack[-1].copy()
        value.update(values)
        self.ctx_stack.append(value)

    def pop(self):
        """Pop last context state"""
        assert len(self.ctx_stack) > 1, "Pop context failed. This is a last context in the stack."
        return self.ctx_stack.pop()
