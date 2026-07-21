# num1, num2 = map(int, input().split())
# if(num1 > num2):
#     print(">")
# elif(num1 < num2):
#     print("<")
# else:
#     print("==")
################################################
# year = int(input())
# yun_year = year % 4 == 0 and year % 100 != 0 or ( year % 400 == 0)
# if yun_year:
#     print(1)
# else:
#     print(0)
# 한 줄에 하나씩 입력되므로 input()을 두 번 사용합니다.
# x = int(input())
# y = int(input())

# # 사분면 판별
# if x > 0 and y > 0:
#     print("1")
# elif x < 0 and y > 0:
#     print("2")
# elif x < 0 and y < 0:
#     print("3")
# elif x > 0 and y < 0:
#     print("4")
# H,M = map(int,input().split())
# if M >= 45:
#     M -= 45
# elif M < 45:
#     H -= 1
#     M += 15
# if H < 0:
#     H = 23
# print(H,M)
dice = list(map(int,input().split()))
if dice[0] == dice[1] == dice[2]:
    print(10000 + dice[0] * 1000)
elif dice[0] == dice[1] or dice[0] == dice[2]:
    print(1000 + dice[0] * 100)
elif dice[1] == dice[2]:
    print(1000 + dice[1] * 100)
else:
    print(max(dice) * 100)
