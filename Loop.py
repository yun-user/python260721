# for looper in [1,2,3,4,5]:
#     print(looper)

# for i in 'abcde':
#     print(i)

# for j in ["americano", "cafe latte", "espresso"]:
#     print(j)

# for i in range(1,10,2):
#     print(i)

# i = 1
# while i < 10:
#     print(i)
#     i += 1

# for i in range(10):
#     if i == 5:
#         break
#     print(i)

# for i in range(10):
#     if i == 5:
#         continue
#     print(i)
# print("End of loop")

# user_input = int(input("구구단 몇 단을 계산할까?:"))

# print("구구단" , user_input,"단을 계산합니다")

# for i in range(1,10):
#     print(user_input, "*" , i, "=" , user_input * i) 

# sentence = "I love you"
# reverse_sentence = ''

# for char in sentence:
#     reverse_sentence = char + reverse_sentence

# print(reverse_sentence)

# decimal = 10
# result = ' '

# while (decimal > 0):
#     remainder = decimal % 2
#     decimal = decimal // 2
#     result = str(remainder) + result
# print(result)
# import random
# guess_number = random.randint(1,100)

# while(True):
#     user_input = int(input("숫자를 맞혀 보세요. (1 ~ 100):"))
#     if user_input > guess_number:
#         print("입력한 숫자가 너무 큽니다.")
#     elif user_input < guess_number:
#         print("입력한 숫자가 너무 작습니다.")
#     else:
#         print("정답입니다.")
#         break


# while(True):
#     user_input = int(input("구구단 몇 단을 계산할까요?:"))
    
#     if user_input == 0:
#         print("구구단 계산을 종료합니다")
#         break

#     elif user_input < 0 or user_input > 9:
#         print("구구단은 1단부터 9단까지 계산할 수 있습니다.")
#         continue

#     print("구구단", user_input,"단을 계산합니다") 
#     for i in range(1,10):
#         print(user_input, " *" , i , "=",user_input * i)

# kor_score = [49,80,20,100,80]
# math_score = [43,60,85,30,90]
# eng_score = [49,82,48,50,100]
# midterm_score = [kor_score, math_score, eng_score]

# student_score = [0,0,0,0,0]
# i = 0
# for subject in midterm_score:
#     for score in subject:
#         student_score[i] += score
#         i += 1
#     i = 0
# else:
#     a,b,c,d,e = student_score
#     student_average = [a/3,b/3,c/3,d/3,e/3]
#     print(student_average)


