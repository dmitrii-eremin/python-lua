class Foo:
    class Bar:
        def __init__(self):
            print("__init__ from Bar")
    
    def __init__(self):
        print("__init__ from Foo")
        Foo.Bar()

Foo()
Foo.Bar()