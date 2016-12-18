def factorial(value):
    return 1 if value == 0 else value * factorial(value - 1)

print(factorial(5))
print(factorial(10))
print(factorial(3))
print(factorial(0))
