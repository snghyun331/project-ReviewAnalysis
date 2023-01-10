import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import datetime

from konlpy.tag import Okt
from konlpy.tag import Twitter
from collections import Counter
from difflib import SequenceMatcher


filename = '/content/drive/MyDrive/2021_Hanium_Review/shoppingReview_DF.csv'
shoppingReview_DF = pd.read_csv(filename)
shoppingReview_DF = shoppingReview_DF.drop('Unnamed: 0', axis=1)
shoppingReview_DF = shoppingReview_DF.dropna()

topicList = sorted(list(set(shoppingReview_DF['topic'])))

def tag_counting(file):
    reviews = file.tolist()
    nlpy = Twitter()

    # 각 문장별로 형태소 구분하기
    sentences_tag = []
    for sentence in reviews:
        morph = nlpy.pos(sentence)
        sentences_tag.append(morph)

    # 명사 or 형용사인 품사만 선별해 리스트에 담기
    noun_adj_list = []
    for sentence in sentences_tag:
        for word, tag in sentence:
            if tag in ['Noun', 'Adjective'] and word not in ['아주', '정말', '모두', '진짜', '완전']:
                noun_adj_list.append(word)

    # 선별된 품사별 빈도수 계산 & 상위 빈도 10위까지 출력
    counts = Counter(noun_adj_list)
    return counts.most_common(10)


# 단어가 유사한 경우, 합쳐서 표시
def similar(tags):
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


for i in range(len(topicList)):
    tags = []
    is_topic = shoppingReview_DF['topic'] == topicList[i]
    tags = tag_counting(file=shoppingReview_DF[is_topic]['review'])
    tags = similar(tags)
    tags.insert(0, topicList[i])
    print(tags)

# 출력예시
# ['가격', ('가격', 12), ('저렴하게 & 저렴하고', 12), ('구매', 4), ('좋은', 3), ('구입', 2), ('착하네요', 1), ('좋아용', 1), ('맘에듭니', 1), ('제품', 1)]
# ['디자인', ('디자인', 14), ('예쁘고', 6), ('이쁘고', 6), ('신발', 5), ('실물', 4), ('깔끔하고', 3), ('좋아요', 3), ('더', 3), ('편해요', 3), ('만족합니다', 3)]
# ['만족도', ('가성', 10), ('비', 9), ('가격', 7), ('대비', 7), ('상품', 5), ('좋아요', 5), ('거', 4), ('제품', 3), ('좋네요', 3), ('같아요', 3)]
# ['착용감', ('편하고', 29), ('좋아요', 21), ('가볍고', 17), ('발', 11), ('착용', 10), ('감', 8), ('좋네요', 7), ('좋습니다', 7), ('신발', 7), ('편해요', 7)]