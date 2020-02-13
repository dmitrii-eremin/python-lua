class A:
    def __type__(self):
        return "atype"
a = A()
print(type(a))
print(type([]))
print(type({}))