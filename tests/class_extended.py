class example:
    def __init__(self, v):
        self.value = v

    def __add__(self, other):
        return example(self.value+other.value)

    def __sub__(self, other):
        return example(self.value-other.value)

    def __mul__(self, other):
        return example(self.value*other.value)

    def __truediv__(self, other):
        return example(self.value/other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return str(self.value)

a = example(5)
b = example(6)
print(a+b)
print(a-b)
print(a*b)
print(a/b)
