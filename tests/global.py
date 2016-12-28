foo = 42

def bar():
    global foo
    foo = 34

print("foo = ", foo)
bar()
print("foo = ", foo)