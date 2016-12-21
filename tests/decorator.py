def strong(old_fun):
    def wrapper(*args):
        s = "<strong>" + old_fun(*args) + "</strong>"
        return s
    return wrapper

def italic(old_fun):
    def wrapper(*args):
        s = "<em>" + old_fun(*args) + "</em>"
        return s
    return wrapper

@italic
@strong
def hello(name):
    return "Hello, " + name + "!"

print(hello("John"))