#아이디와 비밀번호를 뚫고 들어오더라도, 무작위로 생성되는 일회용 비밀번호(OTP)까지 맞춰야만 통과할 수 있는 깐깐한 로그인 시스템
import random
# 클래스 설계: SecureLogin 이라는 클래스를 만들어라.
# class SecureLogin:
#     def __init__(self,username,password):
#         self.username = username
#         self.__password = password
#         self.otp = None
#     비밀 정보 숨기기: 클래스 안에 관리자 아이디는 Public으로 두되, 진짜 비밀번호는 외부에서 절대 볼 수 없게 Private(__) 변수로 꼭꼭 숨겨둬라.
    
#     1차 관문 (로그인 시도): input()을 사용해 사용자에게 아이디와 비밀번호를 입력받아라. 입력받은 아이디와 비밀번호가 모두 일치할 때만(and 사용) 2차 관문으로 넘어간다.
#     def Login(self):
#         input_username = input("아이디를 입력하세요: ")
#         input_password = int(input("비밀번호를 입력하세요: "))
#         if input_username == self.username and input_password == self.__password:
#             print("1차 관문 통과! 2차 관문으로 넘어갑니다.")
#         else:
#             print("아이디 또는 비밀번호가 일치하지 않습니다. 로그인 실패.")
#         2차 관문 (OTP 인증): 1차 관문을 통과했다면 (중첩 if 사용), random.randint()를 이용해 1000부터 9999 사이의 무작위 4자리 보안 코드를 화면에 출력해 줘라.
#         def generate_otp(self):
#             self.otp = str(random.randint(100000, 999999))
#             print(f"생성된 OTP: {self.otp}")
#         generate_otp(self)
#         최종 확인: 사용자에게 방금 나온 보안 코드를 다시 input()으로 입력하게 해서, 완벽히 일치하면 f-string을 사용해 "환영합니다! 시스템 권한을 획득했습니다."라고 멋지게 출력해 주렴. (주의: input()으로 받은 건 글자니까 숫자로 잘 변환해야겠지?)
#         input_otp = int(input("생성된 OTP를 입력하세요: "))
#         if input_otp == int(self.otp):
#             print("환영합니다! 시스템 권한을 획득했습니다.")
#         else:
#             print("OTP가 일치하지 않습니다. 로그인 실패.")
        
# User_1 = SecureLogin("admin",1234)
# User_1.Login()

# 시장의 변동성(확률)을 모의로 돌려보고, 내 주식의 상태를 아주 예쁘게 출력해 보는 포트폴리오 관리기

#부모 클래스 설계: StockAccount 클래스를 만들어라. 초기화할 때 종목명과 나의 평균 단가를 입력받아 저장해
# class StockAccount:
#     def __init__(self, stock_name, avg_price):
#         self.stock_name = stock_name
#         self.avg_price = avg_price
#         self.current_price = avg_price  # 초기 현재 가격은 평균 단가로 설정
#         self.quantity = 0  # 초기 수량은 0으로 설정
    
#     #기본 기능: check_market() 함수를 만들어서, random.random()을 사용해 0.0 ~ 1.0 사이의 확률 값을 뽑아내라. 
#     # 이 값이 0.5보다 크면 "오늘은 장이 좋습니다!"를, 작으면 "오늘은 장이 안 좋습니다."를 출력해라    
#     def check_market(self):
#         market_condition = random.random()
#         if market_condition > 0.5:
#             print("오늘은 장이 좋습니다!")
#         else:
#             print("오늘은 장이 안 좋습니다.")
# # VIP를 위한 진화 (상속과 오버라이딩): StockAccount를 상속받는 VIPAccount 자식 클래스를 만들어라.    
# class VIPAccount(StockAccount):
#     #기능 덮어쓰기: 부모의 check_market() 함수를 오버라이딩해서 기능을 업그레이드해라! 
#     # 단순히 장이 좋고 나쁨만 출력하는 게 아니라, 0.5보다 크거나(or) 내가 가진 종목이 우량주라면 "VIP 고객님, 오늘은 수익 실현하기 좋은 날입니다!"라고 출력
#     def check_market(self):
#         market_condition = random.random()
#         if market_condition > 0.5 or self.stock_name in ["삼성전자", "LG화학", "현대차"]:  # 우량주 예시
#             print("VIP 고객님, 오늘은 수익 실현하기 좋은 날입니다!")
#         else:
#             print("오늘은 장이 안 좋습니다.")
#     # 깔끔한 출력: 마지막으로 내 평단가를 화면에 보여줄 때, f-string을 사용해서 49,864원처럼 천 단위마다 콤마(,)가 예쁘게 찍혀서 나오도록 만들기.
#     def display_avg_price(self):
#         print(f"평균단가: {self.avg_price:,.0f}원")  # 천 단위 콤마와 소수점 없는 형식
        
# stock_1 = StockAccount("삼성전자", 49864)
# stock_1.check_market()
# stock_2 = VIPAccount("LG화학", 75000)
# stock_2.check_market()
# stock_2.display_avg_price()

#보안 관점에서 서버의 접속 기록을 분석하고, 무차별 대입 공격(Brute Force)이나 비정상적인 접근을 찾아내는 미니 보안 스캐너



