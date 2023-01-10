import requests
from bs4 import BeautifulSoup as bs

class movie:
    def __init__(self,url):
        self.url = url               # 영화페이지 URL
        self.static_dict = {}        # 기술통계
        self.List = []               # 전체댓글
        self.List_p = []             # 긍정댓글(평점8이상)
        self.List_n = []             # 부정댓글(평점4이하)

    def get_statics(self):
        raw = requests.get(self.url)
        soup1 = bs(raw.text, 'html.parser')

        # 기자/평론가 평점
        report_stars = soup1.find('div', {'class': "spc_score_area"}).find_all('em')
        report_star = report_stars[1].text + report_stars[2].text + report_stars[3].text + report_stars[4].text

        self.static_dict['기자,평론가 평점'] = report_star