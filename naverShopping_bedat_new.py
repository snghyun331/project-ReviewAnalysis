
'''
사용자 총 평점 -
전체 리뷰 갯수 -
각 리뷰의 작성 시간 -
전체 리뷰 내용 -
주제(카테고리)
주제에 맞는 댓글(밑줄친부분)

총 6 개 크롤링 해오기

+ "재구매", "각 주문별 옵션"  추가 크롤링
'''

from urllib.request import urlopen
from urllib.error import HTTPError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
from collections import Counter

print("START")
scoreset = []
wordset = []
optionset = []
topiccount = []
class naverShopping:
    def __init__(self, link):
        self.link = link
        self.code = 0
    
    # 올바른 링크인지 확인
    def Linkcheck(self):
        if "https://smartstore.naver.com/" not in self.link:
            print("smartstore의 url만 입력이 가능합니다.")          
        else:
            try:
                res = urlopen(self.link)
                if res.status==200:
                    self.code = res.status
                    print("정상 URL 입니다.")
            except HTTPError as e:
                err = e.read()
                code = e.getcode()
                if code == 404:
                    print("요청한 페이지를 찾을 수 없습니다.")
                elif code == 403:
                    print("권한이 없어 접근할 수 없습니다.")
                elif code == 500:
                    print("웹 서버의 오류로 페이지가 제공되지 않습니다.")

        

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



    #전체 댓글 내용, 댓글 작성 시각, 재구매 유무
    def AllwordsTime(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(self.link)
        time.sleep(6)
        
        rev = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > strong > span").text
        rev = rev.replace(",","")
        reviewnum = int(rev)

        time.sleep(1)
        pagenum = (reviewnum // 20) +1 
        print(pagenum)
        print(reviewnum)

        #content > div > div._2-I30XS1lA > div._25tOXGEYJa > div.NFNlCQC2mv > div:nth-child(1) > a > strong
        count = 1
        k=2
        d=2
        
        while(k-1 <= pagenum and count <= reviewnum): #최대(or전체) pagenum
            score = driver.find_elements_by_css_selector('div._37TlmH3OaI em._15NU42F3kT')
            time.sleep(1)
            arti = driver.find_elements_by_css_selector('div.YEtwtZFLDz')
            time.sleep(1)
            date = driver.find_elements_by_css_selector('div._2FmJXrTVEX span._3QDEeS6NLn')
            time.sleep(1)
            options = driver.find_elements_by_css_selector("div._38yk3GGMZq span._3QDEeS6NLn")
            time.sleep(1)

            
            for sc, ar, da, op in zip(score, arti, date, options):    
                scorenum = sc.text
                article = ar.text
                datenum = da.text
                option = op.text
                print("[",k-1,"page," ,count,"] score : ", scorenum, "/ ",datenum, "\n", option, "\n", article)
                scoreset.append(int(scorenum))
                wordset.append(article)
                optionset.append(option)
                
                count +=1
                
                if count >= reviewnum or count %20==1:
                    break
        
            if count %20 ==1 and count != 1: 
                k +=1 
                d +=1
                print("next")
                
                if d==13:
                    d=d-10
                if k==3:
                    driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                    time.sleep(2)
                    driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                    time.sleep(2)
                else:
                    driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a['+str(d)+']').click()
                    time.sleep(2) 

        
        #재구매율
        recount=0
        for i in range(len(wordset)):
            re_1 = wordset[i][0:3]
            re_2 = wordset[i][5:7]
            if re_1 == "재구매":
                recount +=1  
            if re_2 == "재구매":
                recount +=1
        print("재구매횟수 : ", recount,"\n")
        print("재구매율: ", recount/count,"\n")

        #옵션구매순위
        fioptionlist = []
        optiondic = {}
        totaloptionlist = list(set(optionset))
        
        for option in totaloptionlist:
            cnt = optionset.count(option)
            option = option[(option.find(":")+2):]
            optiondic[option] = cnt
            fioptionlist.append(option)
                
        optionsort = sorted(optiondic.items(), key=lambda x:x[1],reverse=True)
        print("옵션 종류", fioptionlist, "\n")
        print("옵션구매순위:", optionsort, "\n")
        
        #옵션별평점 
        optiondic1 = {}
        optiondic2 = {}
        for a in range(len(optionset)):   
            opt = optionset[a][(optionset[a].find(":")+2):]
            optiondic1[opt] = scoreset[a]
            optiondic2 = Counter(optiondic2) + Counter(optiondic1)
            optiondic1 = {}
        
        optiondic3 = {}
        for item in optionsort:
            aversco = optiondic2[item[0]]/item[1]
            optiondic3[item[0]] = round(aversco,2)
                
        print("옵션별평점", optiondic3, "\n")           
            
        
        #except:
        #    print("다음 페이지가 존재하지 않습니다.")
            
        driver.close()



    # 전체 주제, 각 주제별 밑줄 댓글
    def AlltopicWords(self):
    
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(self.link)
        time.sleep(6)
        alltopic = driver.find_elements_by_css_selector("#topic_div")
        time.sleep(1)
                
        num = 0
        count2 = 1
        k2 = 2
        
        alltop = alltopic[0].text.split("\n")
        
        topicscoreset1 = {}
        topicscoreset2 = {}
    
        for i in range(len(alltop)-1): #토픽 넘어갈때마다
            topic = alltop[i+1]
            num +=1
            count2 = 1
            k2 = 2
            d2 = 2
            print(num,":",topic)
            driver.find_element_by_xpath('//*[@id="topic_ul"]/li[' + str(i+2) + ']/a').send_keys(Keys.ENTER)
            time.sleep(1)
            rev = driver.find_element_by_css_selector("span.q9fRhG-eTG").text
            rev = rev.replace(",","")
            reviewnum = int(rev)
            pagenum = (reviewnum // 20) +1 #각 topic 별 리뷰의 총 갯수와 page 갯수
            #page = k2-1
            
            while(k2-1 <= pagenum and count2 <= reviewnum): #최대 몇페이지, 페이지 넘어갈때마다
                topicwords = driver.find_elements_by_css_selector("em._2_otgorpaI")
                time.sleep(1)
                score = driver.find_elements_by_css_selector('div._37TlmH3OaI em._15NU42F3kT')
                time.sleep(1)

                for word, sco in zip(topicwords, score):
                    word = word.text
                    score = sco.text
                    topicscoreset1[topic] = int(score)
                    topicscoreset2 = Counter(topicscoreset2) + Counter(topicscoreset1)
                    topicscoreset1 = {}
                    
                    print("[", topic ,"]", k2-1,"page," ,count2,"\n", "score:", score, "\n", word, "\n")
                    count2 +=1
                    
                    if count2 % 20 ==1 and count2 !=1:
                        k2+=1
                        d2+=1
                        print("next")
                        if d2==13:
                            d2 = d2-10   
                        if k2 ==3:
                            driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                            time.sleep(2)
                            driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[3]').click()
                            time.sleep(2)
                        else:
                            driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a['+str(d2)+']').click()
                            time.sleep(2)

            
            topiccount.append(count2)
                    
        #토픽별평점
        topicaver = {}
        for i in range(len(alltop)-1):
            aver = topicscoreset2[alltop[i+1]]/(topiccount[i]-1)
            topicaver[alltop[i+1]] = round(aver,2)
                
        print("토픽별평점:", topicaver)        
            
        #except:            
        #    print("세부 주제가 존재하지 않습니다.")           
        
        driver.close()
            
        
    
    #시작함수    
    def Start(self):
        self.Linkcheck()
        if self.code ==200:
            #self.AllreviewScore()
            #self.AllwordsTime()
            self.AlltopicWords()
            
        else:
            print("다른 URL을 입력해주십시오.")
            
   
print("END 코드 무결성 확인")

# link = input("댓글을 가져올 URL을 입력하세요. (네이버 스마트스토어만 가능): ")

#Testlink1 = "https://smartstore.naver.com/vanera/products/401437851?NaPm=ct%3Dkrqwfg40%7Cci%3D294c74352bca580307f0ac437cee9ab359fdea69%7Ctr%3Dslsl%7Csn%3D174893%7Chk%3D559ee02d272234ac109281d87c10a94c2127492f"
# ㄴ 리뷰 n만개 링크 : 기본적인 크롤링 및 페이지 넘김, 토픽 넘김 등 검사 : OK
#Testlink2 = "https://smartstore.naver.com/bazig/products/100598948?NaPm=ct%3Dkrrdd5yg%7Cci%3D0b43f79af7bf98343fd58f850cdbb6cdd6a802ed%7Ctr%3Dslsl%7Csn%3D158724%7Chk%3D956cb2a10e428fd86b1bd7b9b5deef169e0aa71d"
# ㄴ 리뷰 n천개 링크 : 각 토픽별 크롤링 중 다음페이지가 없을시 다음 토픽으로 넘겨 크롤링하기 검사 : OK
#Testlink3 = "https://smartstore.naver.com/the-people/products/344686106?NaPm=ct%3Dkrrfqnw0%7Cci%3Dd804bb5ae9f45cf154e492360c5eafd40f151773%7Ctr%3Dslsl%7Csn%3D156754%7Chk%3D12d0b0ffeec743ceaefed2dbcc641b0659d61b11"
# ㄴ 리뷰 n십개 링크 : 기본 페이지 넘김에서 다음페이지가 없을시 리뷰 갯수만큼의 정상 종료후 토픽 크롤링으로 넘어가는지 검사 : OK
#Testlink4 = "https://smartstore.naver.com/sneakeroff/products/5641028211?NaPm=ct%3Dkrrfpp60%7Cci%3Dcfa088c108f28a686816cf6a1b09096d7e1ac800%7Ctr%3Dslsl%7Csn%3D2909031%7Chk%3D6f71d8163787e790f8954ed497b4e2dd5fd150d2"
# ㄴ 리뷰 12개 링크 : 1page 미만일때 정상 종료 후 작동 검사 : OK
Testlink5 = "https://smartstore.naver.com/jemsnewyork/products/5456806874?NaPm=ct%3Dksbn7j9s%7Cci%3D4add5e08580071a21a6639049a211c0b74b9d84c%7Ctr%3Dplac%7Csn%3D631904%7Chk%3Da80e4aef11dde3d9274663f2ef00e877316bafca"
# ㄴ 리뷰 n백개 링크 : 재구매 및 옵션 확인 : OK
Testlink6 = "https://smartstore.naver.com/cureofficial/products/5836750043?NaPm=ct%3Dku9jhzxc%7Cci%3De4c4de09509f2b5bead1d7c291b54203e747c7f2%7Ctr%3Dslsl%7Csn%3D1290373%7Chk%3D5cad510610da1083b9c145794f9966fc334afc4e"
#ㄴ 리뷰 1백개 링크 
#Testlink7="https://smartstore.naver.com/lifedocent/products/5302661232?"
#ㄴ 리뷰 1천개 링크
Testlink8 = "https://smartstore.naver.com/bottlenara/products/5790100298?NaPm=ct%3Dkua30zso%7Cci%3D08afec3a54f1b4f13b162f923e3e6cb9b7c860b3%7Ctr%3Dslsl%7Csn%3D438554%7Chk%3Db03172ba5f5e96cfac52009398714c00e2dc33f4"
#ㄴ리뷰 2백개 링크
Testlink9 = "https://smartstore.naver.com/ladyhola/products/4727172025?NaPm=ct%3Dkvghi17k%7Cci%3D9feaa17b9028069d67df4c9e4bedca936532d81f%7Ctr%3Dslsl%7Csn%3D933885%7Chk%3Df1ab528edfe271ea44411f60fbe7cde333badf03"

Testlink10 = 'https://smartstore.naver.com/alwaysgood/products/4940186727?NaPm=ct%3Dkvlqj9mw%7Cci%3D281f107b2a9eae4c88d7b980710d30488baf7f56%7Ctr%3Dslsbrc%7Csn%3D455826%7Chk%3D5cd144ccdc08ed445f7125887186080d9128fe78'

exam1 = naverShopping(Testlink10)
exam1.Start()

'''
웹페이지 모듈 : 
총 리뷰 갯수, 사용자 총 평점, 재구매율, 토픽별 평점, 제품/옵션별 평점,
토픽분석, 제품/옵션별 구매순위, 댓글작성시간분포, 워드클라우드(주제X)

'''



