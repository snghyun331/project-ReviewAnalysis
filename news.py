# bs4와 셀레니움을 사용하여 크롤링
# 장점: 클린봇 활성, 비활성화 설정 가능. 기술통계 쉽게 가져올 수 있음.
# 단점: 댓글 수가 많아질 수록 많이 느려짐.


import numpy as np
from selenium import webdriver
import time
from bs4 import BeautifulSoup

List = [] #댓글 리스트
des_statics = {} #기술 통계

url = "https://news.naver.com/main/ranking/read.naver?mode=LSD&mid=shm&sid1=001&oid=214&aid=0001139215&rankingType=RANKING"

clean_bot = False # 클린봇 유무

driver = webdriver.Chrome('D:\chromedriver_win32\chromedriver.exe') # () 안에는 chromedriver.exe 위치
driver.implicitly_wait(30)
driver.get(url)

# 뉴스창에서 댓글창으로 넘어가기
btn_more = driver.find_element_by_css_selector('a.u_cbox_btn_view_comment')
btn_more.click()

#만약 clean_bot을 작동시킨다면
if(clean_bot == True):
    btn_clean = driver.find_element_by_css_selector('a.u_cbox_cleanbot_setbutton')
    btn_clean.click()
    clean_bot = driver.find_element_by_css_selector('div.u_cbox_layer_cleanbot2_description').text

    if(clean_bot != '욕설 뿐 아니라 모욕적인 표현이 담긴 댓글까지 AI 기술로 감지하여 자동으로 숨겨줍니다.'): #비활성화일 경우
        btn_check_clean = driver.find_element_by_css_selector('div.u_cbox_layer_cleanbot2_checkboxdummy')
        btn_check_clean.click()

    btn_done_clean = driver.find_element_by_css_selector('div.u_cbox_layer_cleanbot2_extra')
    btn_done_clean.click()

# 만약 clean_bot 비활성화를 시킨다면
else:
    btn_clean = driver.find_element_by_css_selector('a.u_cbox_cleanbot_setbutton')
    btn_clean.click()
    clean_bot = driver.find_element_by_css_selector('div.u_cbox_layer_cleanbot2_description').text

    if (clean_bot == '욕설 뿐 아니라 모욕적인 표현이 담긴 댓글까지 AI 기술로 감지하여 자동으로 숨겨줍니다.'): #활성화 상태면
        btn_check_clean = driver.find_element_by_id('cleanbot_dialog_checkbox_cbox_module')
        btn_check_clean.click()
    
    btn_done_clean = driver.find_element_by_css_selector('div.u_cbox_layer_cleanbot2_extra')
    btn_done_clean.click()

# 댓글 펼치기
while True:
    try:
        btn_more_reply = driver.find_element_by_css_selector('a.u_cbox_btn_more')
        btn_more_reply.click()
        # time.sleep(1)
    except:
        break

# 기술 통계
per = driver.find_elements_by_css_selector('span.u_cbox_chart_per')

male = per[0].text #남자 성비
female = per[1].text #여자 성비

ten = per[2].text #10대
twenty = per[3].text #20대
thirty = per[4].text #30대
forty = per[5].text #40대
fifty = per[6].text #50대
sixty_up = per[7].text #60대 이상


des_statics['남성 비율'] = male
des_statics['여성 비율'] = female
des_statics['10대 비율'] = ten
des_statics['20대 비울'] = twenty
des_statics['30대 비율'] = thirty
des_statics['40대 비율'] = forty
des_statics['50대 비율'] = fifty
des_statics['60대 이상'] = sixty_up

# 댓글 모으기
html = driver.page_source
soup = BeautifulSoup(html,'lxml')
divs = soup.find_all("div",{"class":"u_cbox_area"})

for div in divs:

    time = div.find("span",{"class":"u_cbox_date"}).get_text(strip=True)

    try:
        dic = {}

        reply = int(div.find("span",{"class":"u_cbox_reply_cnt"}).get_text(strip=True))
        comment = div.find("span",{"class":"u_cbox_contents"}).get_text(strip=True)
        sympathy = int(div.find("em",{"class":"u_cbox_cnt_recomm"}).get_text(strip=True))
        anti = int(div.find("em",{"class":"u_cbox_cnt_unrecomm"}).get_text(strip=True))

        dic['댓글내용'] = comment
        dic['대댓글 수'] = reply
        dic['작성시간'] = time
        dic['공감수'] = sympathy
        dic['비공감수'] = anti

        if(sympathy != 0 or anti != 0):
            if (sympathy >anti):
                argu_rate = anti/sympathy
            else:
                argu_rate = sympathy/anti
        else:
            argu_rate = 0
        dic['논란 지수'] = argu_rate


        List.append(dic)

    except:
        comment = np.nan
        sympathy = np.nan
        anti = np.nan

#댓글 리스트 확인
for i in range(30):
    print(List[i])








