def hello(name, age=20, nickname="", *args):
    print("Hello, my name is " + name + " and I'm " + str(age))
    print("My nickname is " + nickname)

hello("John", 12, "antikiller")
hello("Josh", 45)
hello("Jane")
