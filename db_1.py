import sqlite3

#연결 객체 생성

con = sqlite3.connect(":memory:")  # 메모리 상에 임시 데이터베이스 생성
#커서 객체 생성
cur = con.cursor()
# 테이블 생성
cur.execute("CREATE TABLE PhoneBook (Name TEXT, PhoneNumber TEXT);")
# 1건 입력
cur.execute("INSERT INTO PhoneBook VALUES ('홍길동', '123-4567');")
#검색
cur.execute("SELECT * FROM PhoneBook;")
#검색 결과 출력
for row in cur:
    print(row)