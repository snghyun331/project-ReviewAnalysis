import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time

class movie:

    def __init__(self,url):
        self.url = url               # 영화페이지 URL
        self.static_dict = {}        # 기술통계
        self.List = []               # 전체댓글
        self.List_p = []             # 긍정댓글(평점8이상)
        self.List_n = []             # 부정댓글(평점4이하)

    def get_statics(self):
        # selenium                                                                          # 수정
        options = webdriver.ChromeOptions()                                                 # 수정
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')                                               # 수정
        options.add_argument('--window-size=1280x1024')                                     # 수정
        driver = webdriver.Chrome('./chromedriver', options=options)                        # 수정
        driver.get(self.url)                                                                # 수정
        time.sleep(1)                                                                       # 수정

        # 주요정보 페이지에서 평점 페이지로 이동                                            # 수정
        driver.find_element_by_xpath('//*[@id="movieEndTabMenu"]/li[5]/a').click()          # 수정

        # beautifulsoup                                                                     # 수정
        html = driver.page_source                                                           # 수정
        soup1 = bs(html, 'html.parser')                                                     # 수정

        # 네티즌 평점, 문장
        net_star = soup1.find('a', {'id': 'pointNetizenPersentBasic'}).text
        sentence = soup1.find('strong', {'class': 'grp_review'}).text
        self.static_dict['네티즌 평점'] = net_star
        self.static_dict['문장'] = sentence

        # 성별 관람추이
        try:
            path = driver.find_element_by_css_selector('#actualGenderGraph > svg > path:nth-child(3)')
            if path.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector('#actualGenderGraph > svg > text:nth-child(4) > tspan').text
                percen_girl = driver.find_element_by_css_selector('#actualGenderGraph > svg > text:nth-child(6) > tspan').text
                self.static_dict['남자 관람비율'] = percen_boy
                self.static_dict['여자 관람비율'] = percen_girl
        except:
            circle = driver.find_element_by_css_selector('#actualGenderGraph > svg > circle:nth-child(3)')
            if circle.get_attribute('fill') == '#86c8fc':
                percen_boy = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                self.static_dict['남자 관람비율'] = percen_boy
                self.static_dict['여자 관람비율'] = '0%'
            elif circle.get_attribute('fill') == '#ff7e5a':
                percen_girl = driver.find_element_by_css_selector('#actualGenderGraph > svg > text > tspan').text
                self.static_dict['남자 관람비율'] = '0%'
                self.static_dict['여자 관람비율'] = percen_girl

        # 나이별 관람추이
        graphs = soup1.find('div', {'class': 'bar_graph'}).find_all('div', {'class': 'graph_box'})
        for graph in graphs:
            age = graph.find('strong', {'class': 'graph_legend'}).text
            percen_age = graph.find('strong', {'class': 'graph_percent'}).text
            self.static_dict[age + ' 관람비율'] = percen_age

        # 성별 만족도
        boy_star = soup1.find('div', {'class': 'grp_male'}).find('strong').text
        self.static_dict['남자 만족도'] = boy_star
        girl_star = soup1.find('div', {'class': 'grp_female'}).find('strong').text
        self.static_dict['여자 만족도'] = girl_star

        # 나이별 만족도
        grp_ages = soup1.find('div', {'class': 'grp_age'}).find_all('div', {'class': 'grp_box'})
        for grp_age in grp_ages:
            age2 = grp_age.find('strong', {'class': 'graph_legend'}).text
            age2_star = grp_age.find('strong', {'class': 'graph_point'}).text
            self.static_dict[age2 + ' 만족도'] = age2_star

        # 감상포인트
        lis2 = soup1.find('div', {'class': 'grp_sty4'}).find_all('li')
        for li2 in lis2:
            point = li2.find('strong').text
            score = li2.find('span').text
            self.static_dict[point] = score

        return self.static_dict
        driver.close()                                                                    # 수정

    def reviews(self):
        # 각 댓글의 평점, 날짜, 댓글, 공감, 비공감
        url = self.url.replace('basic','point')                                            # 수정
        raw = requests.get(url)                                                            # 수정
        soup1 = bs(raw.text, 'html.parser')                                                # 수정

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
                dict_p = {}
                dict_n = {}
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

                # 전체댓글 추출
                dict['평점'] = rev_star
                dict['날짜'] = rev_date
                dict['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                dict['공감'] = rev_like
                dict['비공감'] = rev_dislike
                self.List.append(dict)

                # if int(rev_star) >= 8:    # 긍정 댓글만 추출
                #     dict_p['평점'] = rev_star
                #     dict_p['날짜'] = rev_date
                #     dict_p['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                #     dict_p['공감'] = rev_like
                #     dict_p['비공감'] = rev_dislike
                #     self.List_p.append(dict_p)
                #
                #
                #
                # if int(rev_star) <= 4:    # 부정 댓글만 추출
                #     dict_n['평점'] = rev_star
                #     dict_n['날짜'] = rev_date
                #     dict_n['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                #     dict_n['공감'] = rev_like
                #     dict_n['비공감'] = rev_dislike
                #     self.List_n.append(dict_n)


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

                    if len(rev) >= 119:
                        try:
                            rev = reple[i].contents[3].contents[1].contents[1]['data-src']
                        except:
                            continue
                    # 좋아요
                    rev_like = like_and_dislike[i].contents[1].contents[5].text
                    # 싫어요
                    rev_dislike = like_and_dislike[i].contents[3].contents[5].text

                # self.review_all_dict[count1] = {'평점': rev_star, '날짜': rev_date,
                #                   '댓글': rev.replace('&#39;', '\'').replace('&#34;', '\"'), '공감': rev_like,
                #                   '비공감': rev_dislike}               # 전체 댓글 추출
                # count1 += 1

                # 전체댓글 추출
                dict['평점'] = rev_star
                dict['날짜'] = rev_date
                dict['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                dict['공감'] = rev_like
                dict['비공감'] = rev_dislike
                self.List.append(dict)

                # if int(rev_star) >= 8:    # 긍정 댓글만 추출
                #     dict_p['평점'] = rev_star
                #     dict_p['날짜'] = rev_date
                #     dict_p['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                #     dict_p['공감'] = rev_like
                #     dict_p['비공감'] = rev_dislike
                #     self.List_p.append(dict_p)
                #
                # if int(rev_star) <= 4:    # 부정 댓글만 추출
                #     dict_n['평점'] = rev_star
                #     dict_n['날짜'] = rev_date
                #     dict_n['댓글'] = rev.replace('&#39;', '\'').replace('&#34;', '\"')
                #     dict_n['공감'] = rev_like
                #     dict_n['비공감'] = rev_dislike
                #     self.List_n.append(dict_n)

        return self.List



######################### 확인용 ######################
# def main():
#     url = movie('https://movie.naver.com/movie/bi/mi/basic.naver?code=190725')
#     statics = url.get_statics()
#     print(statics)
#     reviews = url.reviews()
#     print(reviews)
# 
# main()
