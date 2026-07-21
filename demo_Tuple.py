#Tuple

#함수 정의

# def times(a, b):
#     return a * b, a + b

# result = times(10, 20)

# print(result)

# #print("id: %s , name : %s" %("Kim","김유신") )

# name, age = "김철수", 25

# print(f"이름:{name}, 나이: {age}")

# args = (5,6)
# print(times(*args)) #튜플을 언팩킹하여 함수에 전달

#형식 변환 

# a = set((1,2,3))
# print(type(a))
# print(a)

# print("=================================================")

# b = list(a)
# print(type(b))
# print(b)

# b.append(4)
# print(b)

#딕셔너리

colors = {"apple":"red", "kiwi":"blue"}

colors["banana"] = "yellow"
print(colors)
print(len(colors))

#덮어쓰기
colors["apple"] = "blue"

#삭제
del colors["kiwi"]
print(colors)

#반복문 , items()은 key, value 쌍을 튜플로 반환
for item in colors.items():
    print(item)

