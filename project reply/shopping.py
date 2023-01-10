from urllib.request import urlopen
from urllib.error import HTTPError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import requests
from konlpy.tag import Okt
from collections import Counter
from difflib import SequenceMatcher



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
        doc = {}
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
            driver.implicitly_wait(30)
            driver.get(self.link)
            time.sleep(5)
            allre = driver.find_elements_by_css_selector("strong._2pgHN-ntx6")
            allrevie = allre[0].text
            score = allre[1].text.split('\n')
            print("전체 리뷰 수: ", allrevie)
            print("총 평점 : ", score[0])

            doc['리뷰수'] = allrevie
            doc['평점'] = score[0]

        except:
            print("정보가 조회되지 않습니다.")
        driver.close()
        return doc

    # 전체 댓글 내용, 댓글 작성 시각, 재구매 유무
    def AllwordsTime(self):
        doc={}
        dateset = [] #작성시간을 수집하는 리스트
        scoreset = [] #평점 리스트
        wordset = [] #전체 댓글 리스트를 수집하는 리스트
        optionset = []

        try:
            # 셀레니움 창 숨기면서 크롤링
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
            driver.implicitly_wait(30)
            driver.get(self.link)

            time.sleep(6)

            #리뷰 개수
            rev = driver.find_element_by_css_selector(
                "#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > strong > span").text
            rev = rev.replace(",", "")

            #print(rev)
            reviewnum = int(rev)

            time.sleep(3)

            #페이지 개수
            pagenum = (reviewnum // 20) + 1
            print(pagenum)
            # print(reviewnum)

            count = 1
            k = 2

            while (k - 1 <= pagenum and count <= reviewnum):  # 최대(or전체) pagenum
                score = driver.find_elements_by_css_selector('div._37TlmH3OaI em._15NU42F3kT')
                time.sleep(3)
                arti = driver.find_elements_by_css_selector('div.YEtwtZFLDz')
                time.sleep(3)
                date = driver.find_elements_by_css_selector('div._2FmJXrTVEX span._3QDEeS6NLn')
                time.sleep(3)
                options = driver.find_elements_by_css_selector("div._38yk3GGMZq span._3QDEeS6NLn")
                time.sleep(3)

                for sc, ar, da, op in zip(score, arti, date, options):
                    scorenum = sc.text
                    article = ar.text
                    datenum = da.text
                    option = op.text
                    # #print("[", k - 1, "page,", count, "] score : ", scorenum, "/ ", datenum, "\n", option, "\n",
                    #       article)
                    scoreset.append(int(scorenum)) #평점
                    wordset.append(article) # 리뷰 본문
                    optionset.append(option) #옵션 선택
                    dateset.append(datenum) #작성시간

                    count += 1

                    if count >= reviewnum or count % 20 == 1:
                        break

                if count % 20 == 1 and count != 1:
                    k += 1
                    print("next")
                    if k == 3:
                        driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                        time.sleep(2)
                        driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                        time.sleep(2)
                    else:
                        driver.find_element_by_xpath(
                            '//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[' + str(k) + ']').click()
                        time.sleep(2)


        except:
            print("다음 페이지가 존재하지 않습니다.")

        finally:

            doc['작성시간'] = dateset
            doc['review'] = wordset
            #doc['score'] = scoreset

            # 재구매율
            recount = 0
            for i in range(len(wordset)):
                re_1 = wordset[i][0:3]
                re_2 = wordset[i][5:7]
                if re_1 == "재구매":
                    recount += 1
                if re_2 == "재구매":
                    recount += 1

            #print("재구매횟수 : ", recount, "\n")
            #print("재구매율: ", recount / count, "\n")
            doc['재구매횟수'] = recount

            # 옵션구매순위
            fioptionlist = []
            optiondic = {}
            totaloptionlist = list(set(optionset))

            for option in totaloptionlist:
                cnt = optionset.count(option)
                option = option[(option.find(":") + 2):]
                optiondic[option] = cnt
                fioptionlist.append(option)

            optionsort = sorted(optiondic.items(), key=lambda x: x[1], reverse=True)
            #print("옵션 종류", fioptionlist, "\n")
            #print("옵션구매순위:", optionsort, "\n")
            doc['옵션순위'] = optionsort

            # 옵션별평점
            optiondic1 = {}
            optiondic2 = {}
            for a in range(len(optionset)):
                opt = optionset[a][(optionset[a].find(":") + 2):]
                optiondic1[opt] = scoreset[a]
                optiondic2 = Counter(optiondic2) + Counter(optiondic1)
                optiondic1 = {}

            optiondic3 = {}
            for item in optionsort:
                aversco = optiondic2[item[0]] / item[1]
                optiondic3[item[0]] = round(aversco, 2)

            #print("옵션별평점", optiondic3, "\n")
            doc['옵션평점'] = optiondic3

            driver.close()
            return doc


    # 전체 주제, 각 주제별 밑줄 댓글
    def AlltopicWords(self):
        print("주제모으기시작")
        topiccount = []
        doc = {}
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")

            driver = webdriver.Chrome(ChromeDriverManager().install(),
                                      chrome_options=options)  # () 안에는 chromedriver.exe 위치
            driver.implicitly_wait(30)
            driver.get(self.link)

            # driver = webdriver.Chrome(ChromeDriverManager().install())
            # driver.get(self.link)

            time.sleep(1)
            alltopic = driver.find_elements_by_css_selector("#topic_div")
            time.sleep(1)

            num = 0
            count2 = 1
            k2 = 2
            doc['topic'] = []
            alltop = alltopic[0].text.split("\n")

            topicscoreset1 = {}
            topicscoreset2 = {}

            for i in range(len(alltop) - 1):  # 토픽 넘어갈때마다
                topic = alltop[i + 1]
                num += 1
                count2 = 1
                k2 = 2
                print(num, ":", topic)
                doc['topic'].append(topic)
                doc[str(topic)] = []
                driver.find_element_by_xpath('//*[@id="topic_ul"]/li[' + str(i + 2) + ']/a').send_keys(Keys.ENTER)
                time.sleep(3)
                rev = driver.find_element_by_css_selector("span.q9fRhG-eTG").text
                rev = rev.replace(",", "")
                reviewnum = int(rev)
                pagenum = (reviewnum // 20) + 1

                while (k2 - 1 <= pagenum and count2 <= reviewnum):  # 최대 몇페이지, 페이지 넘어갈때마다
                    topicwords = driver.find_elements_by_css_selector("em._2_otgorpaI")
                    time.sleep(3)
                    score = driver.find_elements_by_css_selector('div._37TlmH3OaI em._15NU42F3kT')
                    time.sleep(3)

                    for word, sco in zip(topicwords, score):
                        word = word.text
                        score = sco.text
                        topicscoreset1[topic] = int(score)
                        topicscoreset2 = Counter(topicscoreset2) + Counter(topicscoreset1)
                        topicscoreset1 = {}

                        #print("[", topic, "]", k2 - 1, "page,", count2, "\n", "score:", score, "\n", word, "\n")
                        count2 += 1
                        doc[str(topic)].append(word)


                        if count2 % 20 == 1 and count2 != 1:
                            k2 += 1
                            print("next")
                            if k2 == 3:
                                driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                                time.sleep(2)
                                driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                                time.sleep(2)
                            else:
                                driver.find_element_by_xpath(
                                    '//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[' + str(k2) + ']').click()
                                time.sleep(2)

                topiccount.append(count2)


        except:
            print("err")

        finally :
            topicaver = {}
            score = []
            for i in range(len(alltop) - 1):
                aver = topicscoreset2[alltop[i + 1]] / (topiccount[i] - 1)
                topicaver[alltop[i + 1]] = round(aver, 2)
                score.append(round(aver, 2))
            print(topicaver)
            doc['평점'] = score
            driver.close()
            return doc

    def tag_counting(self,i,doc):
        topics = doc['topic']
        reviews = doc[str(topics[i])]
        nlpy = Okt()

        # 각 문장별로 형태소 구분하기
        sentences_tag = []
        for sentence in reviews:
            morph = nlpy.pos(sentence,norm=True,stem=True)
            sentences_tag.append(morph)

        # 명사 or 형용사인 품사만 선별해 리스트에 담기
        noun_adj_list = []
        for sentence in sentences_tag:
            for word, tag in sentence:
                if tag in ['Adjective'] and word not in ['아주', '정말', '모두', '진짜', '완전','같다','없다','있다']:
                    noun_adj_list.append(word)

        # 선별된 품사별 빈도수 계산 & 상위 빈도 10위까지 출력
        counts = Counter(noun_adj_list)
        #print(counts.most_common(10))
        return counts.most_common(10)

    def similar(self,tags):
        similar_dict = {}
        del_dict = {}

        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):

                # 두 개의 단어의 유사성을 수치화
                ratio = SequenceMatcher(None, tags[i][0], tags[j][0]).ratio()

                ## ratio 0.75 이상인 경우에만 합치기
                ## ('좋아요', 5) ('좋네요', 3) 좋아요 좋네요 0.6666666666666666
                ## ('좋아요', 5) ('같아요', 3) 좋아요 같아요 0.6666666666666666
                if ratio >= 0.75:
                    # print(tags[i], tags[j], tags[i][0], tags[j][0], ratio)
                    similar_dict[tags[i][0] + ' & ' + tags[j][0]] = tags[i][1] + tags[j][1]
                    del_dict[tags[i][0]] = tags[i][1]
                    del_dict[tags[j][0]] = tags[j][1]

        del_list = list(del_dict)
        tags = dict(tags)
        for i in range(len(del_list)):
            del tags[del_list[i]]

        # 업데이트 후, 정렬
        tags.update(similar_dict)
        tags = sorted(tags.items(), key=lambda item: item[1], reverse=True)

        return tags

    def topicModeling(self,doc):

        topics = doc['topic']
        result = []
        for i in range(len(topics)):
            tags = []
            tags = self.tag_counting(i,doc)
            tags = self.similar(tags)
            result.append(tags)

        return result

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
# if __name__ == '__main__':
#     url = "https://smartstore.naver.com/lifedocent/products/5302661232?"
#     url2 = "https://smartstore.naver.com/the-people/products/344686106?"
#     url3 = "https://smartstore.naver.com/agomall/products/3134115020?NaPm=ct%3Dku6nxlpc%7Cci%3Dadd9a83cddeb4a9dce21985865e11eafe9335e84%7Ctr%3Dsls%7Csn%3D289310%7Chk%3D00243a8ac727bfa1b33da9c6f1f78d2ada2be987"
#     url4="https://smartstore.naver.com/bazig/products/100598948?NaPm=ct%3Dkrrdd5yg%7Cci%3D0b43f79af7bf98343fd58f850cdbb6cdd6a802ed%7Ctr%3Dslsl%7Csn%3D158724%7Chk%3D956cb2a10e428fd86b1bd7b9b5deef169e0aa71d"
#     temp = naverShopping(url2)
#     doc = temp.AlltopicWords()
#     print(doc)