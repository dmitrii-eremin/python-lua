class Animal:
    PLANET = "Earth"

    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print("Hello, my name is: " + self.name + "!")


class Dog(Animal):
    def say_hello(self):
        print("Hello, my name is: " + self.name + "!")
        self.bark()

    def bark(self):
        print("Bark! Bark! Bark!")


sparky = Animal("Sparky")
barky = Dog("Barky")

sparky.say_hello()
barky.say_hello()

barky.bark()

print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)
print("barky.PLANET = ", barky.PLANET)

Animal.PLANET = "Mars"

print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)