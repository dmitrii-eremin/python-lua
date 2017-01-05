"""Class for the symbols stack"""


class SymbolsStack:
    """Class for the symbols stack"""
    def __init__(self):
        self.symbols = [[]]

    def add_symbol(self, name):
        """Add a new symbol to the curent stack"""
        self.symbols[-1].append(name)

    def exists(self, name):
        """Check symbol is exists in the current stack"""
        for stack in self.symbols:
            if name in stack:
                return True
        return False

    def push(self):
        """Push the symbols stack"""
        self.symbols.append([])

    def pop(self):
        """Pop the symbols stack"""
        self.symbols.pop()
