# 함수 연습.py

x = 5

# 함수 정의
def func(a):
    return a + x # 로컬 변수가 없으니까 전역변수 x를 참조

print(func(1)) # 함수 호출
print("=" * 50)
# 함수 정의
def func2(a):
    x = 10 # 로컬 변수 x를 정의
    return a + x # 로컬 변수가 있으니까 전역변수 x를 참조하지 않고 로컬변수 x를 참조

print(func2(1)) # 함수 호출
print("=" * 50)

# return 값이 없는 함수
def setValue(newValue):
    x = newValue 
    print("현재값:", x)
    
retValue = setValue(5) # 함수 호출
print("리턴값:", retValue) # None
print(setValue(5)) # 함수 호출  

# 여러 값 리턴
def swap(x, y):
    return y, x

print(swap(1, 2)) # 함수 호출
print("=" * 50)