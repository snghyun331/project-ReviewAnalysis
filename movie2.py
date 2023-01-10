import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

class naverMovie:

    def __init__(self,url):
        self.url = url

    def get_des(self):

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

        html = driver.page_source
        soup1 = bs(html, 'html.parser')

        # 네티즌. 기자/평론가, 문장
        dict_1 = {}
        net_star = soup1.find('a', {'id': 'pointNetizenPersentBasic'}).text
        sentence = soup1.find('strong', {'class': 'grp_review'}).text
        report_stars = soup1.find('div', {'class': "spc_score_area"}).find_all('em')
        report_star = report_stars[1].text + report_stars[2].text + report_stars[3].text + report_stars[4].text

        dict_1['네티즌 평점'] = net_star
        dict_1['기자/평론가 평점'] = report_star
        dict_1['문장'] = sentence

        # 성별 관람추이
        dict_2 = {}
        try:
            path = driver.find_element_by_css_selector('#actualGenderGraph > svg > path:nth-child(3)')
            if path.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector(
                    '#actualGenderGraph > svg > text:nth-child(4) > tspan').text
                percen_girl = driver.find_element_by_css_selector(
                    '#actualGenderGraph > svg > text:nth-child(6) > tspan').text
                dict_2['남자 관람비율'] = percen_boy
                dict_2['여자 관람비율'] = percen_girl

        except:
            circle = driver.find_element_by_css_selector('#actualGenderGraph > svg > circle:nth-child(3)')
            if circle.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                dict_2['남자 관람비율'] = percen_boy
                dict_2['여자 관람비율'] = '0%'
            elif circle.get_attribute('fill') == '#ff7e5a':
                percen_girl = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                dict_2['여자 관람비율'] = percen_girl
                dict_2['남자 관람비율'] = '0%'

        driver.close()

        #나이별 관람추이
        dict_3 = {}
        graphs = soup1.find('div', {'class': 'bar_graph'}).find_all('div', {'class': 'graph_box'})
        for graph in graphs:
            age = graph.find('strong', {'class': 'graph_legend'}).text
            percen_age = graph.find('strong', {'class': 'graph_percent'}).text
            dict_3[age + ' 관람비율'] = percen_age

        # 성별 만족도
        dict_4 = {}
        boy_star = soup1.find('div', {'class': 'grp_male'}).find('strong').text
        dict_4['남자 만족도'] = boy_star
        girl_star = soup1.find('div', {'class': 'grp_female'}).find('strong').text
        dict_4['여자 만족도'] = girl_star

        #나이별 만족도
        dict_5 = {}
        grp_ages = soup1.find('div', {'class': 'grp_age'}).find_all('div', {'class': 'grp_box'})
        for grp_age in grp_ages:
            age2 = grp_age.find('strong', {'class': 'graph_legend'}).text
            age2_star = grp_age.find('strong', {'class': 'graph_point'}).text
            dict_5[age2 + ' 만족도'] = age2_star

        # 감상포인트
        dict_6 = {}
        lis2 = soup1.find('div', {'class': 'grp_sty4'}).find_all('li')
        for li2 in lis2:
            point = li2.find('strong').text
            score = li2.find('span').text
            dict_6[point] = score

        return dict_1, dict_2, dict_3, dict_4, dict_5, dict_6


    def no_spoiler_all(self):
        List = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict = {}
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

                dict['평점'] = rev_star
                dict['날짜'] = rev_date
                dict['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                dict['공감'] = rev_like
                dict['비공감'] = rev_dislike
                List.append(dict)

        return List

    def no_spoiler_good(self):
        List_g = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict_g = {}
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

                try:
                    if int(rev_star) >= 10:    # 긍정 댓글만 추출
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)
                except:
                    if int(rev_star) >= 8:
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)

        return List_g

    def no_spoiler_bad(self):
        List_b = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict_b = {}
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

                try:
                    if int(rev_star) <= 2:  # 부정 댓글만 추출
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)
                except:
                    if int(rev_star) <= 4:
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)

        return List_b

    def spoiler_all(self):
        List = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict = {}
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

                dict['평점'] = rev_star
                dict['날짜'] = rev_date
                dict['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                dict['공감'] = rev_like
                dict['비공감'] = rev_dislike
                List.append(dict)

        ################## 스포일러 보기 페이지로 넘어가기 ###################
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=Y&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',','')  # 전체 댓글 수

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

                else:  # 관람객X
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

                dict['평점'] = rev_star
                dict['날짜'] = rev_date
                dict['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                dict['공감'] = rev_like
                dict['비공감'] = rev_dislike
                List.append(dict)
        return List

    def spoiler_good(self):
        List_g = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict_g = {}
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

                try:
                    if int(rev_star) >= 10:  # 긍정 댓글만 추출
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)
                except:
                    if int(rev_star) >= 8:
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)

        ################## 스포일러 보기 페이지로 넘어가기 ###################
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=Y&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')  # 전체 댓글 수

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

                else:  # 관람객X
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

                try:
                    if int(rev_star) >= 10:  # 긍정 댓글만 추출
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)
                except:
                    if int(rev_star) >= 8:
                        dict_g['평점'] = rev_star
                        dict_g['날짜'] = rev_date
                        dict_g['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_g['공감'] = rev_like
                        dict_g['비공감'] = rev_dislike
                        List_g.append(dict_g)
        return List_g

    def spoiler_bad(self):
        List_b = []

        if "https://movie.naver.com/movie/bi/mi/basic" in self.url:
            url = self.url.replace('basic', 'point')
            raw = requests.get(url)
        else:
            raw = requests.get(self.url)

        soup1 = bs(raw.text, 'html.parser')

        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        iframe_url = soup1.iframe['src']
        final_url = "https://movie.naver.com" + iframe_url
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=N&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')

        for page in range(1, int(cnt) // 10 + 2):
            url3 = url2 + "&page=" + str(page)
            raw3 = requests.get(url3)
            soup3 = bs(raw3.text, 'html.parser')
            reple = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > p')
            star = soup3.select('body > div > div > div.score_result > ul > li > div.star_score > em')
            like_and_dislike = soup3.select('body > div > div > div.score_result > ul > li > div.btn_area')
            date = soup3.select('body > div > div > div.score_result > ul > li > div.score_reple > dl > dt')

            for i in range(len(reple)):
                dict_b = {}
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

                try:
                    if int(rev_star) <= 2:  # 부정 댓글만 추출
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)
                except:
                    if int(rev_star) <= 4:
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)

        ################## 스포일러 보기 페이지로 넘어가기 ###################
        url2 = final_url.replace(
            '&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false',
            '&type=after&onlyActualPointYn=N&onlySpoilerPointYn=Y&order=sympathyScore')
        soup2 = bs(requests.get(url2).text, 'html.parser')
        cnt = soup2.select('body > div > div > div.score_total > strong > em')[0].text.replace(',', '')  # 전체 댓글 수

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

                else:  # 관람객X
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

                try:
                    if int(rev_star) <= 2:  # 부정 댓글만 추출
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)
                except:
                    if int(rev_star) <= 4:
                        dict_b['평점'] = rev_star
                        dict_b['날짜'] = rev_date
                        dict_b['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                        dict_b['공감'] = rev_like
                        dict_b['비공감'] = rev_dislike
                        List_b.append(dict_b)
        return List_b

    

########### 확인용 ##########

# def main():
#     url = naverMovie('https://movie.naver.com/movie/bi/mi/basic.naver?code=206657')
#     statics = url.get_des()
#     print(statics)
#     spoilergood = url.spoiler_bad()
#     print(spoilergood)
#
# main()