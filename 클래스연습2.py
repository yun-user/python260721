#새로 만든 파일
class Person:
    def __init__(self, person_id, name):
        self.id = person_id
        self.name = name

    def printInfo(self):
        print(f"Person -> id: {self.id}, name: {self.name}")


class Manager(Person):
    def __init__(self, person_id, name, title):
        super().__init__(person_id, name)
        self.title = title

    def printInfo(self):
        print(f"Manager -> id: {self.id}, name: {self.name}, title: {self.title}")


class Employee(Person):
    def __init__(self, person_id, name, skill):
        super().__init__(person_id, name)
        self.skill = skill

    def printInfo(self):
        print(f"Employee -> id: {self.id}, name: {self.name}, skill: {self.skill}")


if __name__ == "__main__":
    people = [
        Person(1, "Alice"),
        Manager(2, "Bob", "Team Lead"),
        Employee(3, "Charlie", "Python"),
        Person(4, "Diana"),
        Manager(5, "Ethan", "Project Manager"),
        Employee(6, "Fiona", "Data Analysis"),
        Person(7, "George"),
        Manager(8, "Hannah", "Engineering Manager"),
        Employee(9, "Ian", "DevOps"),
        Employee(10, "Julia", "UI/UX"),
    ]

    print("=== 10개 인스턴스 정보 출력 ===")
    for p in people:
        p.printInfo()
