import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

class naverMovie:

    def __init__(self,url):
        self.url = url

    def get_des(self):

        dict={}
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280x1024')

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(self.url)
        time.sleep(1)
        # 주요정보 페이지에서 평점 페이지로 이동
        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            driver.find_element_by_xpath('//*[@id="movieEndTabMenu"]/li[5]/a').click()

        raw = requests.get(self.url)
        soup1 = bs(raw.text, 'html.parser')

        net_star = soup1.find('a', {'id': 'pointNetizenPersentBasic'}).text
        sentence = soup1.find('strong', {'class': 'grp_review'}).text

        dict['네티즌평점'] = net_star
        dict['문장'] = sentence

        try:
            path = driver.find_element_by_css_selector('#actualGenderGraph > svg > path:nth-child(3)')
            if path.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector(
                    '#actualGenderGraph > svg > text:nth-child(4) > tspan').text
                percen_girl = driver.find_element_by_css_selector(
                    '#actualGenderGraph > svg > text:nth-child(6) > tspan').text
                dict['남자 관람비율'] = percen_boy
                dict['여자 관람비율'] = percen_girl

        except:
            circle = driver.find_element_by_css_selector('#actualGenderGraph > svg > circle:nth-child(3)')
            if circle.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                dict['남자 관람비율'] = percen_boy
                dict['여자 관람비율'] = '0%'
            elif circle.get_attribute('fill') == '#ff7e5a':
                percen_girl = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                dict['여자 관람비율'] = percen_girl
                dict['남자 관람비율'] = '0%'

        driver.close()

        graphs = soup1.find('div', {'class': 'bar_graph'}).find_all('div', {'class': 'graph_box'})
        for graph in graphs:
            age = graph.find('strong', {'class': 'graph_legend'}).text
            percen_age = graph.find('strong', {'class': 'graph_percent'}).text
            dict[age + ' 관람비율'] = percen_age

        # 성별 만족도
        boy_star = soup1.find('div', {'class': 'grp_male'}).find('strong').text
        dict['남자 만족도'] = boy_star
        girl_star = soup1.find('div', {'class': 'grp_female'}).find('strong').text
        dict['여자 만족도'] = girl_star

        #나이별 만족도
        grp_ages = soup1.find('div', {'class': 'grp_age'}).find_all('div', {'class': 'grp_box'})
        for grp_age in grp_ages:
            age2 = grp_age.find('strong', {'class': 'graph_legend'}).text
            age2_star = grp_age.find('strong', {'class': 'graph_point'}).text
            dict[age2 + ' 만족도'] = age2_star

        # 감상포인트
        lis2 = soup1.find('div', {'class': 'grp_sty4'}).find_all('li')
        for li2 in lis2:
            point = li2.find('strong').text
            score = li2.find('span').text
            dict[point] = score
        return dict

    def no_spoiler_all(self):

        raw = requests.get(self.url)
        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감, 논란지수
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        dict_7 = dict()
        count1 = 0


        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                if (reple[i].contents[3] == ' 스포일러 컨텐츠로 처리되는지 여부 '):  # 관람객
                    if (reple[i].contents[5].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[5].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[5].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                else:  # 관람객X
                    if (reple[i].contents[3].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[3].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[3].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                dict_7[count1] = {'평점': rev_star, '날짜': rev_date,
                                  '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                                  '비공감': rev_dislike, '논란지수': contro}  # 전체 댓글 추출
                count1 += 1


        pd.DataFrame(dict_7).T

        return dict_7

    def no_spoiler_good(self):
        raw = requests.get(self.url)
        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감, 논란지수
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        dict_7 = dict()
        count1 = 0

        dict_8 = dict()
        count2 = 0

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                if (reple[i].contents[3] == ' 스포일러 컨텐츠로 처리되는지 여부 '):  # 관람객
                    if (reple[i].contents[5].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[5].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[5].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                else:  # 관람객X
                    if (reple[i].contents[3].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[3].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[3].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                dict_7[count1] = {'평점': rev_star, '날짜': rev_date,
                                  '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                                  '비공감': rev_dislike, '논란지수': contro}  # 전체 댓글 추출

                if int(rev_star) >= 8:  # 긍정 댓글만 추출
                    dict_8[count2] = {'평점': rev_star, '날짜': rev_date,
                                      '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                                      '비공감': rev_dislike, '논란지수': contro}
                    count2 += 1

        pd.DataFrame(dict_8).T
        return dict_8

    def no_spoiler_bad(self):

        raw = requests.get(self.url)
        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감, 논란지수
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        dict_7 = dict()
        count1 = 0

        dict_8 = dict()
        count2 = 0

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                if (reple[i].contents[3] == ' 스포일러 컨텐츠로 처리되는지 여부 '):  # 관람객
                    if (reple[i].contents[5].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[5].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[5].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                else:  # 관람객X
                    if (reple[i].contents[3].text.strip() == '스포일러가 포함된 감상평입니다. 감상평 보기'):
                        continue
                    else:
                        # 평점
                        rev_star = star[i].text
                        # 날짜
                        rev_date = date[0].contents[3].text.strip()[:10]
                        # 댓글
                        rev = reple[i].contents[3].text.strip()
                        # 댓글이 119자 이상일 때
                        if len(rev) >= 119:
                            try:
                                rev = reple[i].contents[3].contents[1].contents[1]['data-src']
                            except:
                                continue
                        # 좋아요
                        rev_like = like_and_dislike[i].contents[1].contents[5].text
                        # 싫어요
                        rev_dislike = like_and_dislike[i].contents[3].contents[5].text
                        # 논란지수
                        if (rev_like == '0') and (rev_dislike != '0'):
                            contro = int(rev_dislike)
                        elif rev_like != '0':
                            contro = round(int(rev_dislike) / int(rev_like), 4)

                dict_7[count1] = {'평점': rev_star, '날짜': rev_date,
                                  '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                                  '비공감': rev_dislike, '논란지수': contro}  # 전체 댓글 추출

                if int(rev_star) <= 4:  # 긍정 댓글만 추출
                    dict_8[count2] = {'평점': rev_star, '날짜': rev_date,
                                      '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                                      '비공감': rev_dislike, '논란지수': contro}
                    count2 += 1

            pd.DataFrame(dict_8).T
            return dict_8