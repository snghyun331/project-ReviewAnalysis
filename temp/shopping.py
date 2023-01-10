from urllib.request import urlopen
from urllib.error import HTTPError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import requests


class naverShopping:
    def __init__(self, link):
        self.link = link
        self.code = 0

    # 올바른 링크인지 확인
    def Linkcheck(self):

        if "https://smartstore.naver.com/" not in self.link and "https://news.naver.com/" not in self.link and "https://movie.naver.com/" not in self.link:
            return 0
        else:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}

                res = requests.get(self.link, headers=headers)

                if res.status_code == 200:
                    self.code = res.status_code
                    return 1
                elif res.status_code == 404:
                    self.code = res.status_code
                    return 2
                elif res.status_code == 403:
                    self.code = res.status_code
                    return 3
                elif res.status_code == 500:
                    self.code = res.status_code
                    return 4

            except HTTPError as e:
                err = e.read()
                return err

    # 전체 리뷰 수, 총 평점
    def AllreviewScore(self):
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(self.link)
            time.sleep(5)
            allre = driver.find_elements_by_css_selector("strong._2pgHN-ntx6")
            allrevie = allre[0].text
            score = allre[1].text.split('\n')
            print("전체 리뷰 수: ", allrevie)
            print("총 평점 : ", score[0])
        except:
            print("정보가 조회되지 않습니다.")
        driver.close()

    # 전체 댓글 내용, 댓글 작성 시각
    def AllwordsTime(self):
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(self.link)
            time.sleep(6)
            arti = driver.find_elements_by_css_selector('div.YEtwtZFLDz')
            time.sleep(3)
            date = driver.find_elements_by_css_selector('div._2FmJXrTVEX span._3QDEeS6NLn')
            time.sleep(3)
            reviewnum = int(driver.find_element_by_css_selector("span.q9fRhG-eTG").text)
            time.sleep(2)
            pagenum = (reviewnum // 20) + 1
            print(pagenum)
            print(reviewnum)

            count = 1
            k = 2

            while (k - 1 <= pagenum and count <= reviewnum):  # 최대(or전체) pagenum
                if count % 20 == 1 and count != 1:
                    k += 1
                    print("next")
                    driver.find_element_by_xpath(
                        '//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[' + str(k) + ']').click()
                    time.sleep(3)
                    arti = driver.find_elements_by_css_selector('div.YEtwtZFLDz')
                    time.sleep(3)
                    date = driver.find_elements_by_css_selector('div._2FmJXrTVEX span._3QDEeS6NLn')
                    time.sleep(3)

                for ar, da in zip(arti, date):
                    article = ar.text
                    datenum = da.text
                    print("[", k - 1, "page,", count, "]", datenum, "\n", article)
                    count += 1

                    if count >= reviewnum or count % 20 == 1:
                        break



        except:
            print("다음 페이지가 존재하지 않습니다.")

        driver.close()

    # 전체 주제, 각 주제별 밑줄 댓글
    def AlltopicWords(self):
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(self.link)
            time.sleep(7)
            alltopic = driver.find_elements_by_css_selector("#topic_div")
            time.sleep(4)

            num = 0
            count2 = 1
            k2 = 2

            alltop = alltopic[0].text.split("\n")

            for i in range(len(alltop) - 1):  # 토픽 넘어갈때마다
                topic = alltop[i + 1]
                num += 1
                count2 = 1
                k2 = 2
                print(num, ":", topic)
                driver.find_element_by_xpath('//*[@id="topic_ul"]/li[' + str(i + 2) + ']/a').send_keys(Keys.ENTER)
                time.sleep(3)
                topicwords = driver.find_elements_by_css_selector("em._2_otgorpaI")
                time.sleep(3)
                reviewnum = int(driver.find_element_by_css_selector("span.q9fRhG-eTG").text)
                time.sleep(2)
                pagenum = (reviewnum // 20) + 1  # 각 topic 별 리뷰의 총 갯수와 page 갯수
                # page = k2-1

                while (k2 - 1 <= pagenum and count2 <= reviewnum):  # 최대 몇페이지, 페이지 넘어갈때마다
                    if count2 % 20 == 1 and count2 != 1:
                        print("next")
                        driver.find_element_by_xpath(
                            '//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[' + str(k2) + ']').click()
                        time.sleep(3)
                        topicwords = driver.find_elements_by_css_selector("em._2_otgorpaI")
                        time.sleep(3)

                    for word in topicwords:
                        word = word.text
                        print("[", topic, "]", k2 - 1, "page,", count2, "\n", word)
                        count2 += 1

                        if count2 >= reviewnum or count2 % 20 == 1:
                            k2 += 1
                            break


        except:
            print("세부 주제가 존재하지 않습니다.")

        driver.close()

    # 시작함수
    def Start(self):
        self.Linkcheck()
        if self.code == 200:
            self.AllreviewScore()
            self.AllwordsTime()
            self.AlltopicWords()

        else:
            print("다른 URL을 입력해주십시오.")


# print("END 코드 무결성 확인")
#
# # link = input("댓글을 가져올 URL을 입력하세요. (네이버 스마트스토어만 가능): ")
# # Testlink1 = "https://smartstore.naver.com/vanera/products/401437851?NaPm=ct%3Dkrqwfg40%7Cci%3D294c74352bca580307f0ac437cee9ab359fdea69%7Ctr%3Dslsl%7Csn%3D174893%7Chk%3D559ee02d272234ac109281d87c10a94c2127492f"
# # ㄴ 리뷰 n만개 링크 : 기본적인 크롤링 및 페이지 넘김, 토픽 넘김 등 검사 : OK
# # Testlink2 = "https://smartstore.naver.com/bazig/products/100598948?NaPm=ct%3Dkrrdd5yg%7Cci%3D0b43f79af7bf98343fd58f850cdbb6cdd6a802ed%7Ctr%3Dslsl%7Csn%3D158724%7Chk%3D956cb2a10e428fd86b1bd7b9b5deef169e0aa71d"
# # ㄴ 리뷰 n천개 링크 : 각 토픽별 크롤링 중 다음페이지가 없을시 다음 토픽으로 넘겨 크롤링하기 검사 : OK
# # Testlink3 = "https://smartstore.naver.com/the-people/products/344686106?NaPm=ct%3Dkrrfqnw0%7Cci%3Dd804bb5ae9f45cf154e492360c5eafd40f151773%7Ctr%3Dslsl%7Csn%3D156754%7Chk%3D12d0b0ffeec743ceaefed2dbcc641b0659d61b11"
# # ㄴ 리뷰 n십개 링크 : 기본 페이지 넘김에서 다음페이지가 없을시 리뷰 갯수만큼의 정상 종료후 토픽 크롤링으로 넘어가는지 검사 : OK
#Testlink4 = "https://smartstore.naver.com/sneakeroff/products/5641028211?NaPm=ct%3Dkrrfpp60%7Cci%3Dcfa088c108f28a686816cf6a1b09096d7e1ac800%7Ctr%3Dslsl%7Csn%3D2909031%7Chk%3D6f71d8163787e790f8954ed497b4e2dd5fd150d2"
# # ㄴ 리뷰 12개 링크 : 1page 미만일때 정상 종료 후 작동 검사
# Testlink5 = "https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid"
# exam1 = naverShopping(Testlink5)
# print(exam1.Linkcheck())
# # exam1.Start()