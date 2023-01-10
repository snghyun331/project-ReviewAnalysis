import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import datetime

from konlpy.tag import Okt
from konlpy.tag import Twitter
from collections import Counter

filename = '/content/drive/MyDrive/2021_Hanium_Review/shoppingReview_DF.csv'
shoppingReview_DF = pd.read_csv(filename)
shoppingReview_DF = shoppingReview_DF.drop('Unnamed: 0', axis=1)
shoppingReview_DF = shoppingReview_DF.dropna()

# shoppingReview_DF

topicList = sorted(list(set(shoppingReview_DF['topic'])))

def tag_counting(file):
  string_list = []
  string_list = "\n\n".join(file)

  nouns = []
  nouns = nlpy.nouns(string_list)
  if '아주' in nouns:
    nouns.remove('아주')
  if '정말' in nouns:
    nouns.remove('정말')
  if '모두' in nouns:
    nouns.remove('모두')
  if '진짜' in nouns:
    nouns.remove('진짜')
  if '완전' in nouns:
    nouns.remove('완전')

  from collections import Counter
  count = Counter(nouns)

  tag_count = []
  tags = []

  for n, c in count.most_common(100):
	  dics = {'tag': n, 'count': c}

	  if len(dics['tag']) >= 2 and len(tags) <= 49:
	    tag_count.append(dics)
	    tags.append(dics['tag'])

  # for tag in tag_count:
  #   print(" {:<14}".format(tag['tag']), end='\t')
  #   print("{}".format(tag['count']))

  return tag_count


for i in range(len(topicList)):
  tags = []
  is_topic = shoppingReview_DF['topic'] == topicList[i]
  tags = tag_counting(file = shoppingReview_DF[is_topic]['review'])
  tags.insert(0, topicList[i])
  print(len(tags) - 1, tags)