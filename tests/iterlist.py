a = [1, 4, 8, 16, 52, 34, 78, 342]

k = 0

strange_sum = 0
for i in a:
    k += 1
    if k > 3:
        break

    print("Current i is: ", i)
    strange_sum += i

print("After break: ")

for i in a:
    print("Current i is: ", i)
    strange_sum += i

print("Some strange sum is: ", strange_sum)