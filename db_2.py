import sqlite3

#연결 객체 생성(raw string 사용): 영구적으로 파일 저장
con = sqlite3.connect(r"c:\work\sample.db") 

#커서 객체 생성
cur = con.cursor()

# 테이블 생성, 문장이 끝나면 ;을 붙이는것을 권장
cur.execute("CREATE TABLE PhoneBook (Name TEXT, PhoneNum TEXT);")

# 1건 입력 ,홍길동이 Name Text, 010-123-4567이 PhoneNum Text에 들어감
cur.execute("INSERT INTO PhoneBook VALUES ('홍길동', '010-123-4567');")

#입력 파라메타 처리 , (?,?)은 파라메타 자리 표시자, 튜플로 전달 
name = '김철수'
phoneNum = '010-987-6543'
cur.execute("INSERT INTO PhoneBook VALUES (?, ?);", (name, phoneNum))

#여러건 입력, executemany()를 사용하여 여러건을 한꺼번에 입력
data = [
    ('이영희', '010-111-2222'),
    ('박민수', '010-333-4444'),
    ('최지우', '010-555-6666')
]
cur.executemany("INSERT INTO PhoneBook VALUES (?, ?);", data)

#검색, PhoneBook 테이블에 있는 모든 데이터를 검색
cur.execute("SELECT * FROM PhoneBook;")

#검색 결과 출력
for row in cur:
    print(row)
    
#쓰기 작업을 완료했으면 반드시 commit()을 호출해야 실제 DB에 반영됨
con.commit()
con.close()