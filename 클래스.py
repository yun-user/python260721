# 클래스 연습.py

class Person:# 클래스 정의
    # 초기화 메서드
    def __init__(self):
        self.name = "default name"
    def printInfo(self):
        print(f"My name is {self.name}")

# 인스턴스 생성
p1 = Person()
p2 = Person()
p2.name = "전우치"



p1.printInfo() # 메서드 호출
p2.printInfo() # 메서드 호출
        