class Animal:
    def __init__(self,name):
        self.name = name
    def talk(self):
        raise NotImplementedError("Subclasses must implement this method")

class Cat(Animal):
    def talk(self):
        return "Meow"
    
class Dog(Animal):
    def talk(self):
        return "Woof"
    
animals = [Cat("Whiskers"), Dog("Fido")]

for animal in animals:
    print(f"{animal.name} : {animal.talk()}")