#부모 클래스(공통 코드)
class Person:
    def __init__(self, name, phoneNumber):
        self.name = name
        self.phoneNumber = phoneNumber

    def printInfo(self):
        print("Info(Name:{0}, Phone Number: {1})".format(self.name, self.phoneNumber))
    def working(self):
        print("Person is working")

#자식 클래스(약간 더 구체적인 코드)
class Student(Person):
    #덮어쓰기(재정의, overriding)
    def __init__(self, name, phoneNumber, subject, studentID):
        #부모 클래스의 생성자를 호출
        super().__init__(name, phoneNumber)
        self.subject = subject
        self.studentID = studentID
    #덮어쓰기(재정의, overriding)
    def printInfo(self):
        print("Info(Name:{0}, Phone Number: {1}, Subject: {2}, Student ID: {3})".format(self.name, self.phoneNumber, self.subject, self.studentID))

p = Person("전우치", "010-222-1234")
s = Student("이순신", "010-111-1234", "컴공", "991122")
p.printInfo()
s.printInfo()
s.working() # 자식 클래스에서 부모 클래스의 메소드를 그대로 사용 가능
# print(p.__dict__)
# print(s.__dict__)


