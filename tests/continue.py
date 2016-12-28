for i in range(10):
    if i == 5:
        continue
    for j in range(10):
        if j == 7:
            continue
        print(i, " * ", j, " = ", i * j)