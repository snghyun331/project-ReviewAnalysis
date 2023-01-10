import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import urllib.request
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from collections import Counter
from konlpy.tag import Mecab
from tqdm import tqdm
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, Dense, LSTM, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

#instance = text_Sentimental2.Model()
#instance.sentiment_predict("아 진짜 재미없다..")
#instance.sentiment_predict("완전 재미있어요. 마음에 드네요!!")
#instance.sentiment_predict("드디어 오류를 고쳤다. 행복하다.. 이제 잘수있다.")
#instance.sentiment_predict("파이팅하세요!")

new_sentence = "파이팅하세요!"

def sentiment_predict(new_sentence):
    okt = Okt()
    stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
    max_len = 35

    dfset = pd.read_csv("sentimental_train_data.csv")
    npset = dfset.to_numpy()

    dataset = []
    for sentence in npset:
        nan_removed_sentence = [word for word in sentence if str(word) != 'nan'] 
        dataset.append(nan_removed_sentence)

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(dataset)
    print("OK")
    threshold = 3
    total_cnt = len(tokenizer.word_index)
    rare_cnt = 0
    total_freq = 0 
    rare_freq = 0

    for key, value in tokenizer.word_counts.items():
        total_freq = total_freq + value

        # 단어의 등장 빈도수가 threshold보다 작으면
        if(value < threshold):
            rare_cnt = rare_cnt + 1
            rare_freq = rare_freq + value

    vocab_size = total_cnt - rare_cnt + 1

    tokenizer = Tokenizer(vocab_size) 
    tokenizer.fit_on_texts(dataset)

    loaded_model = load_model('best_model.h5')
    new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', new_sentence)
    new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
    new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
    encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
    pad_new = pad_sequences(encoded, maxlen = max_len) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측
    if(score > 0.5):
        print("{:.2f}% 확률로 긍정 리뷰입니다.\n".format(score * 100))
    else:
        print("{:.2f}% 확률로 부정 리뷰입니다.\n".format((1 - score) * 100))
        
sentiment_predict(new_sentence)
        

