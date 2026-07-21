# BankAccount.py

#은행의 계정을 표현한 클래스 
class BankAccount:
    def __init__(self, id, name, balance):
        #인스턴스 멤버 변수를 내부에서 사용할 수 있도록 private으로 선언
        # 앞에만 __를 붙이면 외부에서 접근할 수 없게 된다.
        self.__id = id
        self.__name = name 
        self.__balance = balance 
    def deposit(self, amount):
        self.__balance += amount 
    def withdraw(self, amount):
        self.__balance -= amount
    
    # 지금 인스턴스 상태를 문자열로 반환하는 메소드
    def __str__(self):
        return "{0} , {1} , {2}".format(self.__id, self.__name, self.__balance)

#인스턴스 객체를 생성
account1 = BankAccount(100, "전우치", 15000)
account1.deposit(5000)
account1.withdraw(3000)
print(account1)

#외부에서 접근 -> private 멤버 변수에 접근하려고 하면 에러 발생
#print(account1.__balance)#외부에서 접근이 안되기 때문에 에러 발생
#print(account1._BankAccount__balance)#private 멤버 변수에 접근하려면 클래스명_변수명으로 접근해야 한다.
########################################