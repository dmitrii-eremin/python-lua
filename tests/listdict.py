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

print(a[1])
print(b[0][1])
print(c["firstname"], c["lastname"])

ch = c["children"][0]
print(ch["name"], ch["age"])