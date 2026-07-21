f = open("06_yesterday.txt", "r")#읽기 모드
yesterday_lyrics = f.readlines()#파일을 한 줄씩 읽어 리스트에 저장
f.close() #파일 닫기

contents = ""

for line in yesterday_lyrics:#문장들을 line에 담음
    contents += line.strip() + "\n" #줄바꿈 추가 ,strip()은 양쪽 끝 공백 제거 -> 전체가 하나의 문장처럼 붙음

print(contents)#실제로 출력되는건 한줄로 붙어있음
n_of_yesterday = contents.upper().count("YESTERDAY")#대문자로 바꿔서 카운트
#print("number of yesterday:",n_of_yesterday)#대문자 YESTERDAY 카운트
print(f"number of yesterday:{n_of_yesterday}".format(n_of_yesterday))#f-string 사용

