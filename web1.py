# 웹 크롤링
from bs4 import BeautifulSoup

#페이지를 로딩(rt: read text)
page = open("Chap09_test.html", "rt", encoding="utf-8")




#검색이 용이한 객체
soup = BeautifulSoup(page, "html.parser")
#print(soup.prettify()) # html 문서를 보기 좋게 출력

#<p>태그를 몽땅 검색
#print(soup.find_all("p")) #리스트로 변환

#<p class = "outer-text">태그를 검색
#print(soup.find_all("p",class_="outer-text")) #class 속성이 outer-text인 p태그만 검색

#attrs 속성 더 많이 사용
#print(soup.find_all("p",attrs={"class":"outer-text"})) #class 속성이 outer-text인 p태그만 검색

#태그 내부에 문자열만 추출
for item in soup.find_all("p"):
    title = item.text.strip() #strip() : 문자열 양쪽 공백 제거
    #치환
    title = title.replace("\n"," ") #\n 제거
    print(title)
