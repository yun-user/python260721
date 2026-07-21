# student_number = int(input())

# for i in range(student_number):
#     nums = list(map(int,input().split()))
#     average = sum(nums[1:])/nums[0]
#     count = 0
#     for j in range(1,nums[0]+1):
#         if nums[j] > average:
#             count += 1
#     rate = (count / nums[0]) * 100
#     print(f"{rate:.3f}%")
#백준 문제(??!)
# ID = list(input().split()) #ID를 입력
# for i in range(len(ID)):
#     check_ID = ID[i].lower()
#     if check_ID == ID[i]:
#         print(ID[i]+"??!")
#     else:
#         print("")
#1998년생인 내가 태국에서는 2541년생?!
# 태국의 연도 계산 방식에 따라 543을 더해야 함
# 1998 + 543 = 2541
# year = int(input())
# print(year - 543)
# A + B + C
A,B,C = list(map(int,input().split()))
print(A + B + C)