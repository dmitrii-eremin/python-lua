class A:
    pass
a = A()
if isinstance(a,A) and type(a) is A:
    print("class typing works")
d = []
if type(d) is list and isinstance(d,list):
    print("list type works")
e = {}
if type(e) is dict and isinstance(e,dict):
    print("dict type works")
if type(d) is dict or type(e) is list:
    print("not good")