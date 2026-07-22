import random


# number = random.random()


# print(number)  # 0.0 ~ 1.0 사이의 난수 생성
# print(number)
# print(random.uniform(2.0,5.0))
# print([random.randrange(20) for i in range(10)])  # 0 ~ 19 사이의 난수 생성
# print(random.sample(range(20),5)) # 0 ~ 19 사이의 난수 5개 생성

#로또번호 만들기
print(random.sample(range(1,46),6))  # 1 ~ 45 사이의 난수 6개 생성

from os.path import *
print("절대경로:",abspath("python.exe"))  # 절대경로
print("파일명:",basename("C:\\Python313\\python.exe"))  # 파일명
fileName = "C:\\Python313\\python.exe"
if exists(fileName):
    print("파일이 존재합니다.")
    print("파일 크기:",getsize(fileName))  # 파일 크기
else:
    print("파일이 존재하지 않습니다.")
    
import os
print("운영체제명:",os.name)

#파일목록
import glob
#print("파일목록:",glob.glob(r"c:\work\*.py"))  # c:\work\ 폴더의 모든 .py 파일 목록
