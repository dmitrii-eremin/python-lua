def foo():
    pass

def varargs(name, *args):
    print("Name is: ", name)
    print(*args)

varargs("first", 1, 3, 6, 4, 7)
varargs("second", "hello", "python", "world")