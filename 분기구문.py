# 분기구문.py

score = int(input("점수를 입력하세요:"))

# 분기

if 90 <= score <= 100:
    grade = "A"
    print(f"{grade}학점입니다.")
elif 80 <= score < 90:
    grade = "B"
    print(f"{grade}학점입니다.")
else:
    grade = "C"
    print(f"{grade}학점입니다.")
    
print(f"등급은 {grade}입니다.")