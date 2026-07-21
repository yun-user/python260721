# 반복구문.py

value = 5

while value > 0:
    print(value, end = " ")
    value -= 1

print("\n--- for in 구문---")
lst = [10,20,30]

for item in lst:
    print(item, end = " ")
    
name = {"\n성함":"전우치", "나이":30, "주소":"서울시"}

for item in name:
    print(item, end = " ")
    
#수열 함수
print("수열 함수")
print(list(range(10)))
print(list(range(1, 13))) #월
print(list(range(2000, 2027))) #연도
print(list(range(1, 32))) #날

#리스트 컴프리핸션(함축)

lst = list(range(1, 11))
print([i ** 2 for i in lst if i > 5])

colors = {100:"red", 200:"green", 300:"blue"}
print([v.upper() for v in colors.values()])

