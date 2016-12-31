a = [i * j for i in range(5) for j in range(3) if i * j % 2 == 0 and i > 0 and j > 0]

for item in a:
    print(item)

b = {i: i ** 2 for i in range(5)}

for k, v in b.items():
    print(k, v)