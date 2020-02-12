
a = [i * j for i in range(5) for j in range(3) if i * j % 2 == 0 and i > 0 and j > 0]

for item in a:
    print(item)

lst = ["a","b","c","d","e"]
b = {lst[i]: i ** 2 for i in range(5)}

for k in lst:
    print(k,b[k])