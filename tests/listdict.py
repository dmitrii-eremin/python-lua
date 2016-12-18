a = [1, 2, 5]
b = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

c = {
    "firstname": "John",
    "lastname": "Doe",
    "age": 42,
    "children": [
        {
            "name": "Sara",
            "age": 4,
        },
    ],
}

print(a[2])
print(b[1][2])
print(c["firstname"], c["lastname"])

ch = c["children"][1]
print(ch["name"], ch["age"])