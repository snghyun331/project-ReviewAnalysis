import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
from datetime import datetime


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}

d_list = []
now = datetime.now()
date = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)
print("date " + date)

def ranking(date, url) :
    html = requests.get(url, headers=headers).text
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
            d['date'] = date
            d['review_count'] = int(Memo(d['src']))

            d_list.append(d)

def Memo(url):
    oid = url.split("oid=")[1].split("&")[0]
    aid = url.split("aid=")[1]
    page = 1

    headers = {
        'Referer':url,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
        page) + "&refresh=false&sort=FAVORITE"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    total_comm = str(soup).split('comment":')[1].split(",")[0]
    return total_comm


url = "https://news.naver.com/main/ranking/popularDay.nhn?date=" + date
ranking(date, url)
# print("1 : ", len(d_list))

url = "https://news.naver.com/main/ranking/popularMemo.nhn?date=" + date
ranking(date, url)
# print("2 : ", len(d_list))

newD_list = []
for i in d_list:
    if i not in newD_list:
        newD_list.append(i)

df = pd.DataFrame(newD_list)
df = df.sort_values(by='review_count', ascending=False)
df_new = df[0:5]
print(df_new)