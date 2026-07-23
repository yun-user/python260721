# web2.py 
#클리앙의 중고장터를 크롤링 
#웹크롤링을 위한 라이브러리 
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request 
#특정 문자열을 검색하기 위한 정규표현식
import re 

#User-Agent를 조작하는 경우(아이폰에서 사용하는 사파리 브라우져의 헤더) 
hdr = {'User-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.23 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'}

#파일에 저장
f = open("todayhumor.txt", "wt", encoding="utf-8")


#페이징 처리 추가
for i in range(1, 11): #1~10페이지까지 크롤링
    url = "https://www.todayhumor.co.kr/board/list.php?table=bestofbest&page=" + str(i) #맨 뒤의 page=1,2,3,4,5,6,7,8,9,10 페이지를 의미
    print(url)
    #웹브라우저의 헤더를 추가 
    req = urllib.request.Request(url, headers=hdr)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, 'html.parser')
    lst = soup.find_all('td', attrs={'class': 'subject'})
    #한번 더 <a>태그를 검색
    for tag in lst:
        title = tag.find('a').text.strip()
        print(title)
        f.write(title + "\n")

f.close()
print("저장완료")

#선택한 영역을 주석처리: ctrl + / 
#<td class="subject">
    #<a href="/board/view.php?table=bestofbest&amp;no=483461&amp;s_no=483461&amp;page=1" target="_top">치과에 충치치료받던 관우같은 아이</a>
#</td>   
