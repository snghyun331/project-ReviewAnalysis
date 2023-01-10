import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
from datetime import datetime
from operator import itemgetter



class get_ranking:
    def __init__(self):
        self.d_list = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
        now = datetime.now()
        self.date = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)


    def Memo(self,url):
        oid = url.split("oid=")[1].split("&")[0]
        aid = url.split("aid=")[1]
        page = 1

        headers = {
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }

        url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
            page) + "&refresh=false&sort=FAVORITE"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        total_comm = str(soup).split('comment":')[1].split(",")[0]
        return total_comm

    def ranking(self,url):
        html = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'html.parser')
        ranking_total = soup.find_all(class_='rankingnews_box')

        for item in ranking_total:
            media = item.a.strong.text
            news = item.find_all(class_="list_content")
            # print(news)
            for new in news:
                d = {}
                d['media'] = media
                d['src'] = "https://news.naver.com/" + new.a['href']
                d['title'] = new.a.text
                d['date'] = self.date
                d['review_count'] = int(self.Memo(d['src']))

                self.d_list.append(d)

    def result(self):

        url = "https://news.naver.com/main/ranking/popularMemo.nhn?date=" + self.date
        self.ranking(url)

        newD_list = []
        for i in self.d_list:
            if i not in newD_list:
                newD_list.append(i)

        s_list = sorted(newD_list,key=itemgetter('review_count'),reverse=True)
        News_list = s_list[0:5]

        return News_list


# if __name__ == '__main__':
#     test = get_ranking()
#     list = test.result()
#     print(list)