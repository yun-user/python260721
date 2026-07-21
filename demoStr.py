#demoStr.py

strC = """이 문자열은 
 여러 라인으로
 구성되어 있습니다
"""

# for i in range(len(strC)):
#     print(strC[i], end = " ")

#리스트

# lst = ["red", "green", "blue"]

# print(lst)

# #lst의 길이
# print(len(lst))

# #yellow 추가
# lst.append("yellow")
# print(lst)

# #green 제거
# lst.remove("green")
# print(lst)

# #black, white 추가 -> 확장
# lst.extend(["black", "white"])
# print(lst)

# #정렬
# lst.sort()
# print(lst)

#set(집합)

# a = {1, 2, 3, 3}
# b = {3, 4, 4, 5}

# print("a 출력: "+ str(a))
# print(type(a))
# print(a.union(b)) #합집합
# print(a.intersection(b)) #교집합
# print(a.difference(b)) #차집합

#튜플

# tp = (100,200,300)

# print("tp 타입?" + str(type(tp)))
# print(len(tp))
# print(tp[0])
# print("300의 인덱스는?: " + str(tp.index(300)))
# print("200의 개수는?: " + str(tp.count(200)))