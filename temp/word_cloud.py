# 단어구름에 필요한 라이브러리를 불러옵니다.
from wordcloud import WordCloud
# 한국어 자연어 처리 라이브러리를 불러옵니다.

# 명사의 출현 빈도를 세는 라이브러리를 불러옵니다.
from collections import Counter
# 그래프 생성에 필요한 라이브러리를 불러옵니다.
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


class wordcloud:
    def __init__(self,text):
        self.text = text

    # def get_tags(self,max_count,min_length):
    #     t = Kkma()
    #     nouns = t.nouns(self.text)
    #     processed = [n for n in nouns if len(n) >= min_length]
    #     count = Counter(processed)
    #     result={}
    #
    #     for n,c in count.most_common(max_count):
    #         result[n] = c
    #
    #     if len(result) == 0:
    #         result['내용이 없습니다.'] = 1
    #
    #     return result


    def make_cloud_image(self,file_name):

        no = {"더", "합니다", "입니다", "진짜", "하는", "없다", "너무", "정말", "이제", "지금","이게","좀"}
        font_path = 'static/font/BMDOHYEON_ttf.ttf'
        icon = np.array(Image.open('./static/assets/img/cloud.png'))

        wc = WordCloud(font_path=font_path, background_color='white', width=800, height=600,stopwords=no,mask=icon)
        wc = wc.generate(self.text)
        fig = plt.figure(figsize=(20, 15))
        plt.imshow(wc,aspect="auto")
        plt.axis('off')

        fig.savefig("static/assets/{0}.png".format(file_name))


    # def process_from_text(self,max_count,min_length):
    #     # tags = self.get_tags(max_count,min_length)
    #
    #     #단어가중치
    #     # for n,c in words.items():
    #     #
    #     #     if n in tags:
    #     #         tags[n] = tags[n]*int(words[n])
    #
    #     self.make_cloud_image("wordcloud")

