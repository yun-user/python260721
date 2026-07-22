# 아이디랑 비밀번호를 뚫고 들어와도 OTP까지 맞춰야 로그인할 수 있게 하는 클래스
#OTP 만들때 사용할 모듈
# import random

# #id랑 비밀번호 입력
# input_id = input("아이디를 입력하세요: ")
# input_password = input("비밀번호를 입력하세요: ")

# class SecureLogin:
#     def __init__(self):
#         #관리자 ID는 Public으로 설정, 진짜 비밀번호와 OTP는 Private으로 설정
#         self.UserID = "admin"
#         self.__Password = "password"
#         self.__OTP = random.randint(100000, 999999) # 6자리 OTP 생성
    
#     def login(self, input_id, input_password):
#         if input_id == self.UserID and input_password == self.__Password:
#             print("아이디와 비밀번호가 일치합니다.")
#             print(f"OTP가 생성되었습니다: {self.__OTP}")
#             user_otp = int(input("OTP를 입력하세요: "))
#             if user_otp == self.__OTP:
#                 print("로그인 성공!")
#             else:
#                 print("OTP가 일치하지 않습니다. 로그인 실패.")
#         else:
#             print("아이디 또는 비밀번호가 일치하지 않습니다. 로그인 실패.")


# login_system = SecureLogin()
# login_system.login(input_id, input_password)
#hangman
# question = list("batman")
# lst = []
# #question의 길이만큼 "_"를 lst에 추가
# for i in range(0, len(question)):
#     lst.append("_")
# print(lst)
# #횟수 제한
# num_of_try = 10
# while num_of_try > 0:
#     #사용자에게 문자 입력받기
#     user_input = input("문자를 입력하세요: ")
#     #입력한 문자가 question에 있는지 확인
#     if user_input in question:
#         print("맞았습니다!")
#         #question에서 user_input이 있는 위치를 찾아서 lst에 user_input으로 바꿔주기
#         for i in range(0, len(question)):
#             if question[i] == user_input:
#                 lst[i] = user_input
#         print(lst)
#         #lst에 "_"가 없으면 게임 종료
#         if "_" not in lst:
#             print("게임 승리!")
#             break
#     else:
#         print("틀렸습니다.")
#         num_of_try -= 1
#         print(f"남은 횟수: {num_of_try}")

#reverse
# value = "Hello World"
# value_list = list(value)
# value_list.reverse()
# print("".join(value_list))#쪼개져서 뒤집힌 글자들 사이에 아무것도 넣지 않고 끈끈하게 붙여서 다시 하나의 문장으로 완성한다.

#실제 데이터를 다루는 금융 프로그램이야. 시장의 변동성(확률)을 모의로 돌려보고, 내 주식의 상태를 아주 예쁘게 출력해 보는 포트폴리오 관리기를 만들어 볼 거야.
# import random
# #1. 부모 클래스 설계 
# class StockAccount:
#     def __init__(self, Company_name, Stock_price):
#         self.Company_name = Company_name
#         self.Stock_price = Stock_price

#     def check_market(self):
#         check_point = random.random() #0과 1사이의 랜덤한 숫자 생성
#         if check_point < 0.5:
#             print("오늘은 장이 안좋습니다")
#         elif check_point > 0.5:
#             print("오늘은 장이 좋습니다")
# #2. 자식 클래스 설계 (부모 클래스 상속)
# class VIPAccount(StockAccount):
#     def __init__(self, Company_name, Stock_price, VIP_level):
#         super().__init__(Company_name, Stock_price) #부모 클래스의 __init__ 메서드 호출
#         self.VIP_level = VIP_level

#     def check_market(self):
#         #오버라이딩 (부모 클래스의 메서드를 자식 클래스에서 재정의)
#         #부모와 똑같은 이름으로 함수를 다시 만들면 , 파이썬은 자식 버전을 실행! 
#         check_point = random.random() #0과 1사이의 랜덤한 숫자 생성
        
#         # 미리 정해둔 '우량주' 리스트 (여기에 실리콘투를 넣어보자!)
#         blue_chip_stocks = ["실리콘투", "삼성전자", "SK하이닉스"]
        
#         if check_point > 0.5 or self.Company_name in blue_chip_stocks:
#             print(f"VIP 고객님 오늘은 수익 실현하기 좋은 날입니다!(시장점수:{check_point:.2f})")
#         else:
#             print(f"VIP 고객님 오늘은 조금 조심하시는 게 좋겠습니다.(시장점수:{check_point:.2f})")
# account = StockAccount("삼성전자",400000)
# vip_account = VIPAccount("실리콘투", 100000, "Gold")
# account.check_market()
# vip_account.check_market()

#나만의 자동 가계부 시스템
# import csv
# #거래기록 => 상품명, 거래금액, 거래일자, 거래유형(수입/지출) 등등 // 거래 1건을 저장하는 클래스, 예를 들면 "김밥 / 5000원 / 2023-08-01 / 지출 / 식비" 이런 식으로 저장
# class Transaction:
#     #__init__()은 객체가 생성될 때 자동으로 실행되는 메서드
#     def __init__(self, name, price, date, transaction_type, category, memo=""): # memo=""라고 되어 있기 때문에 메모를 입력하지 않아도 기본값은 빈 문자열.
#         self.name = name #상품명
#         self.price = price #거래금액
#         self.date = date #거래일자
#         self.transaction_type = transaction_type #거래유형(수입/지출)
#         self.category = category #거래카테고리(식비,교통비 등등)
#         self.memo = memo #거래메모

# #가계부 전체를 관리하는 클래스, 거래기록을 담는 리스트와 통계 기능을 포함
# #즉 거래 여러 건을 모아둔 가계부
# class AccountBook:
#     def __init__(self):
#         self.transactions = [] #거래기록을 담을 리스트
#         self.total_income = 0 #총 수입
#         self.total_expense = 0#총 지출

#     def add_transaction(self,transaction): #거래 기록 추가 메서드
#         self.transactions.append(transaction) #transaction 객체를 transactions 리스트에 추가
#         if transaction.transaction_type == "수입":
#             self.total_income += transaction.price
#         else: #"수입"이 아니면 다 지출로 간주
#             self.total_expense += transaction.price

#     def show_all_transactions(self): #지금까지 저장된 모든 거래기록을 출력
#         for transaction in self.transactions:
#             print(f"상품명: {transaction.name}, 거래금액: {transaction.price}, 거래일자: {transaction.date}, 거래유형: {transaction.transaction_type}, 거래카테고리: {transaction.category}, 거래메모: {transaction.memo}")

#     def show_statistics(self): # 통계 메서드
#         print("\n=== 📊 VIP 통계 및 분석 ===")
#         print(f"총 거래 건수: {len(self.transactions)}건") #거래 리스트에 있는 거래 개수, Tramsactoion 객체의 개수를 세는 것
#         print(f"총 수입: {self.total_income:,}원")
#         print(f"총 지출: {self.total_expense:,}원")
#         print(f"잔액: {self.total_income - self.total_expense:,}원")
#         print("-" * 25)

#         # 1. 카테고리별 지출을 담을 빈 딕셔너리 준비
#         expense_by_category = {}

#         # 2. 리스트를 for문으로 돌면서 확인, 거래 리스트에 있는 거래를 하나씩 꺼내서 t에 저장
#         for t in self.transactions:
#             # 3. '지출'인 영수증만 골라내기 (조건문)
#             if t.transaction_type == "지출":
#                 # 4. 딕셔너리에 해당 카테고리가 이미 있으면 금액을 누적(+=)하고, 없으면 새로 추가(=)
#                 if t.category in expense_by_category:
#                     expense_by_category[t.category] += t.price
#                 else:
#                     expense_by_category[t.category] = t.price

#         # 5. 깔끔하게 화면에 출력하기
#         print("[ 💸 카테고리별 지출 내역 ]")
#         if not expense_by_category:
#             print("아직 기록된 지출 내역이 없습니다. 텅~")
#         else: #지출 내역이 있을 때만 카테고리별 지출 내역을 출력
#             for category, amount in expense_by_category.items(): #items()를 사용하면 딕셔너리의 key와 value를 동시에 가져올 수 있음
#                 # {amount:,} 를 사용하면 50000 -> 50,000 처럼 천 단위 콤마가 찍혀서 보기 좋습니다!
#                 print(f"- {category}: {amount:,}원")
#         print("===========================\n")

#     #저장하기 : 리스트 -> csv 파일로 저장 //현재 가계부 데이터를 csv 파일로 저장하는 메서드
#     def save_to_file(self):
#         with open("가계부.csv","w", encoding = "utf-8", newline = "") as file: #newline = ""를 지정하면, 줄 사이에 빈 줄이 생기지 않게 해줌
#             writer = csv.writer(file)#CSV 파일에 데이터를 쓰기 위해 csv.writer 객체를 생성
#             for t in self.transactions:
#                 writer.writerow([t.name,t.date,t.price,t.date,t.transaction_type,t.category,t.memo]) #csv.writer를 써서 데이터를 리스트 형태로 묶어 writerow()로 한 줄씩 파일에 저장,
#                 #이때 각각이 row[0], row[1], row[2]... 이런 식으로 저장됨
#         print("데이터가 가계부.csv 파일에 안전하게 저장되었습니다! 💾")
    
#     #불러오기 : 파일 -> 리스트
#     def load_from_file(self): #이전에 저장했던 가계부.csv 파일을 다시 불러오는 기능
#         try:
#             # 'r'은 읽기(Read) 모드야.
#             with open("가계부.csv", "r", encoding="utf-8") as file:
                
#                 reader = csv.reader(file)#CSV파일을 한 줄씩 읽어오는 도구
#                 # 파일에서 한 줄씩(row) 읽어와서
#                 for row in reader:
#                     if not row:
#                         continue  # 빈 줄은 건너뛰기
#                     # row[0]은 이름, row[1]은 거래금액, row[2]은 거래일자, row[3]은 거래유형, row[4]은 거래카테고리, row[5]은 거래메모
#                     # 이걸 다시 Transaction 객체로 묶어서 가계부 리스트에 추가해!
#                     # (주의: 파일에서 읽어온 숫자는 문자열 취급이니 int()로 꼭 바꿔줘야 해)
#                     loaded_t = Transaction(row[0], int(row[1]), row[2], row[3], row[4],row[5])
#                     self.add_transaction(loaded_t)
                
#             print("이전 가계부 데이터를 성공적으로 불러왔습니다! 📖")
        
#         except FileNotFoundError:
#             #만약 파일이 없다면 당황하지 않고 자연스럽게 넘어가기!
#             print("저장된 가계부 파일이 없습니다. 새로운 가계부를 시작합니다. ✨")    
# catalog = AccountBook() #가계부 객체 생성

# catalog.load_from_file() #프로그램 시작 시 가장 먼저 기존 데이터를 불러온다

# while(True):
#     print("\n=== 나만의 자동 가계부 시스템 ===")
#     print("1. 거래기록 추가")
#     print("2. 거래기록 조회")
#     print("3. 통계")
#     print("4. 종료")
#     choice = input("선택: ")

#     if choice == "1":
#         name = input("상품명: ")
#         price = int(input("거래금액: "))
#         date = input("거래일자: ")
#         transaction_type = input("거래유형(수입/지출): ")
#         category = input("거래카테고리(식비,교통비 등등): ")
#         memo = input("거래메모: ")
        
#         transaction = Transaction(name, price, date, transaction_type, category, memo) #Transaction 객체 생성
        
#         catalog.add_transaction(transaction)
#         print("거래기록이 성공적으로 추가되었습니다!")

#     elif choice == "2":
#         catalog.show_all_transactions()
    
#     elif choice == "3":
#         # 통계 기능 구현
#         catalog.show_statistics()
#     elif choice == "4":
#         # 2. 종료하기 전에 안전하게 데이터를 파일에 저장합니다.
#         catalog.save_to_file()
#         print("가계부 프로그램을 종료합니다. 안녕히 가세요!")
#         break
#     else:
#         print("잘못된 선택입니다.")

# 보안 관점에서 서버의 접속 기록을 분석하고, 무차별 대입 공격(Brute Force)이나 비정상적인 접근을 찾아내는 미니 보안 스캐너

#LogParser 클래스와 ThreatDetector 클래스를 분리하여 설계
class LogParser:
    log_list = ["192.168.0.1 - FAIL", "10.0.0.2 - SUCCESS", "192.168.0.1 - FAIL"] #더미 로그 리스트
    def __init__(self,):


class ThreatDetector:
    def __init__(self):







