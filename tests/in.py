a = [1, 2, 3, 4]
b = {
    "name": "John",
    "age": 42,
}

c = "Hello, world!"

if 2 < 3:
    print("2 < 3")

print(1 in a)
print(2 in a)
print(5 in a)
print("name" in b)
print("surname" in b)
print("Hell" in c)
print("world" in c)
print("Foo" in c)
print("Hells" not in c)