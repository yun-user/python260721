class SmartPhone:
    def __init__(self):
        # 1. Public (공용) : 제한 없음! 누구나 알 수 있는 내 폰 기종
        self.model_name = "최신형 파이썬폰" 
        
        # 2. Protected (보호됨) : 가족/지인에게만 알려주는 와이파이 비번 (밑줄 1개)
        self._wifi_password = "우리집_비밀번호123" 
        
        # 3. Private (비밀) : 절대 철통 보안! 내 은행 앱 비밀번호 (밑줄 2개)
        self.__bank_password = "7777"

    # 💡 [핵심 포인트] 
    # Private 변수는 밖에서는 못 보지만, 클래스 '안'에서는 얼마든지 쓸 수 있어!
    # 그래서 이렇게 내부 함수를 통해서만 안전하게 확인하도록 만들어야 해.
    def pay_with_phone(self, input_password):
        print("\n--- 💳 결제 시도 ---")
        if input_password == self.__bank_password:
            print("결제가 정상적으로 완료되었습니다! 💸")
        else:
            print("경고: 비밀번호가 틀렸습니다! 결제 실패 🚨")

# ---------------------------------------------------------
# 자, 이제 내가 스마트폰을 하나 샀다고 치자! (객체 생성)
my_phone = SmartPhone()

# 1️⃣ Public 변수에 접근해 보기 (누구나 볼 수 있음)
print(f"내 폰 기종은? : {my_phone.model_name}")
# 출력 결과: 내 폰 기종은? : 최신형 파이썬폰


# 2️⃣ Protected 변수에 접근해 보기 (가급적 건드리지 말라는 경고!)
print(f"우리 집 와이파이 비번은? : {my_phone._wifi_password}")
# 출력 결과: 우리 집 와이파이 비번은? : 우리집_비밀번호123
# (파이썬의 특징: 에러는 안 나고 보이긴 하지만, 밖에서 직접 부르는 건 아주 나쁜 매너야!)


# 3️⃣ Private 변수에 접근해 보기 (철통 보안 작동!)
# print(my_phone.__bank_password) 
# 🚨 만약 위 코드의 주석(#)을 풀고 실행하면? 
# AttributeError: 'SmartPhone' object has no attribute '__bank_password' 
# 라는 무시무시한 빨간색 에러가 뜨면서 프로그램이 죽어버려! 
# 밖에서는 이름표를 아예 떼어버려서 찾을 수가 없거든.


# 4️⃣ Private 변수를 올바르게 사용하는 방법!
# 밖에서 직접 변수를 들여다보는 대신, 안전하게 만들어둔 '내부 기능(함수)'을 이용하는 거야.
my_phone.pay_with_phone("1234")  # 틀린 비밀번호 입력
my_phone.pay_with_phone("7777")  # 맞는 비밀번호 입력