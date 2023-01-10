from bs4 import BeautifulSoup
import requests
import re
import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from operator import itemgetter
from collections import Counter
import platform

import io
import urllib,base64

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from wordcloud import STOPWORDS


# articleTitle
class naverNews:

    def __init__(self, url):
        self.url = url
        self.List = []  # 댓글 리스트
        self.des_statics = {}  # 기술 통계

    def get_title(self):
        header = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            "referer": self.url,
        }
        resp = requests.get(self.url,headers=header)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one('#articleTitle').text
        return title

    # 기술 통계를 가져오는 부분
    # 남성 비율, 여성 비율, 10대 비율, 20대 비율, 30대 비율, 40대 비율, 50대 비율, 60대 이상 비율

    def get_des(self):

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)  # () 안에는 chromedriver.exe 위치
        driver.implicitly_wait(30)
        driver.get(self.url)

        # 뉴스창에서 댓글창으로 넘어가기
        btn_more = driver.find_element_by_css_selector('a.u_cbox_btn_view_comment')
        btn_more.click()

        per = driver.find_elements_by_css_selector('span.u_cbox_chart_per')

        male = per[0].text  # 남자 성비
        female = per[1].text  # 여자 성비

        ten = per[2].text  # 10대
        twenty = per[3].text  # 20대
        thirty = per[4].text  # 30대
        forty = per[5].text  # 40대
        fifty = per[6].text  # 50대
        sixty_up = per[7].text  # 60대 이상

        self.des_statics['남성 비율'] = male
        self.des_statics['여성 비율'] = female
        self.des_statics['10대 비율'] = ten
        self.des_statics['20대 비율'] = twenty
        self.des_statics['30대 비율'] = thirty
        self.des_statics['40대 비율'] = forty
        self.des_statics['50대 비율'] = fifty
        self.des_statics['60대 이상'] = sixty_up

        return self.des_statics

    # 여러 리스트들을 하나로 묶어 주는 함수입니다.
    def flatten(self, l):
        flatList = []
        for elem in l:
            # if an element of a list is a list
            # iterate over this list and add elements to flatList
            if type(elem) == list:
                for e in elem:
                    flatList.append(e)
            else:
                flatList.append(elem)
        return flatList

    def clean_bot_reply(self):

        oid = self.url.split("oid=")[1].split("&")[0]  # 422
        aid = self.url.split("aid=")[1]  # 0000430957

        page = 1
        header = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            "referer": self.url,
        }

        while True:
            c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
                page) + "&refresh=false&sort=FAVORITE"
            # 파싱하는 단계입니다.
            r = requests.get(c_url, headers=header)

            cont = BeautifulSoup(r.content, "html.parser")

            total_comm = str(cont).split('comment":')[1].split(",")[0]

            match = re.findall('"contents":([^\*]*),"userIdNo"', str(cont))
            replyCount = re.findall('"replyAllCount":([^\*]*),"replyPreviewNo"', str(cont))  # 답글 개수
            regTime = re.findall('"modTime":([^\*]*),"modTimeGmt"', str(cont))  # 시간
            sympathyCount = re.findall('"sympathyCount":([^\*]*),"antipathyCount"', str(cont))  # 공감수
            antipathyCount = re.findall('"antipathyCount":([^\*]*),"hideReplyButton"', str(cont))  # 비공감수
            hiddenByCleanbot = re.findall('"hiddenByCleanbot":([^\*]*),"score"', str(cont))  # 클린봇 감지 여부

            for i in range(len(match)):
                dic = {}
                dic['댓글내용'] = match[i]
                dic['대댓글 수'] = replyCount[i]
                dic['작성시간'] = regTime[i]
                dic['공감수'] = sympathyCount[i]
                dic['비공감수'] = antipathyCount[i]
                dic['논란수치'] = 0
                if (int(sympathyCount[i]) != 0 or int(antipathyCount[i] != 0)):
                    if (int(sympathyCount[i]) > int(antipathyCount[i])):
                        dic['논란수치'] = int(antipathyCount[i]) / int(sympathyCount[i])
                    elif (int(antipathyCount[i]) > int(sympathyCount[i])):
                        dic['논란수치'] = int(sympathyCount[i]) / int(antipathyCount[i])

                else:
                    dic['논란수치'] = 0

                dic['감지여부'] = hiddenByCleanbot[i]

                self.List.append(dic)

            # 한번에 댓글이 20개씩 보이기 때문에 한 페이지씩 몽땅 댓글을 긁어 옵니다.
            if int(total_comm) <= ((page) * 20):
                break
            else:
                page += 1

        allComments = self.flatten(self.List)

        return allComments








