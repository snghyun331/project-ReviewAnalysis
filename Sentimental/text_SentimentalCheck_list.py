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

new_sentence = ["파이팅하세요!", "영화 진짜 재미없었어요. 괜히 봤어요.", "안녕하세요."]
new_sentence1 = ["진짜노잼", "영화 진짜 재미있어요.", "좋아요."]

new_sentence = pd.Series(new_sentence)
print(new_sentence)

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

    vocab_size = 24749

    tokenizer = Tokenizer(vocab_size) 
    tokenizer.fit_on_texts(dataset)

    ########################################

    loaded_model = load_model('best_model.h5')
    
    new_sentence = new_sentence.str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")

    predictset = []
    for sentence in tqdm(new_sentence):
        tokenized_sentence = okt.morphs(sentence, stem=True) # 토큰화
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stopwords] # 불용어 제거
        predictset.append(stopwords_removed_sentence)
    ###
    
    predictset = np.array(predictset)
    
    encoded = tokenizer.texts_to_sequences(predictset) # 정수 인코딩
    
    pad_new = pad_sequences(encoded, maxlen = max_len) # 패딩
    score = loaded_model.predict(pad_new) # 예측
    
    for sc in score:
        if(float(sc) > 0.5):
            print("{:.2f}% 확률로 긍정 리뷰입니다.\n".format(float(sc) * 100))
        else:
            print("{:.2f}% 확률로 부정 리뷰입니다.\n".format((1 - float(sc)) * 100))

        
sentiment_predict(new_sentence)