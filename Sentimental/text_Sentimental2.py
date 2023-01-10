import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import urllib.request
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split #문제발생
from collections import Counter
from konlpy.tag import Mecab
from tqdm import tqdm
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, Dense, LSTM, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
class Model():
    
    def Model_create(self):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt", filename="ratings_train.txt")
        urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_test.txt", filename="ratings_test.txt")
        urllib.request.urlretrieve("https://raw.githubusercontent.com/bab2min/corpus/master/sentiment/steam.txt", filename="steam.txt")
        train_data = pd.read_table('ratings_train.txt')
        test_data = pd.read_table('ratings_test.txt')
        total_game_data = pd.read_table('steam.txt', names=['label', 'document'])

        train_game_data2, test_game_data2 = train_test_split(total_game_data, test_size = 0.25, random_state = 42)

        train_data = pd.concat([train_data, train_game_data2])
        test_data = pd.concat([test_data, test_game_data2])

        train_data = train_data.sample(frac=1).reset_index(drop=True).drop(['id'],axis=1)
        test_data = test_data.sample(frac=1).reset_index(drop=True).drop(['id'],axis=1)

        print('전처리 전 훈련용 샘플의 수 :',len(train_data))
        print(train_data['document'].nunique(), train_data['label'].nunique())
        train_data.drop_duplicates(subset = ['document'], inplace=True) 
        train_data['document'] = train_data['document'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
        train_data['document'] = train_data['document'].str.replace('^ +', "") 
        train_data['document'].replace('', np.nan, inplace=True) # 공백은 Null 값으로 변경
        train_data = train_data.dropna(how='any') # Null 값 제거
        print(train_data.isnull().sum())
        print('전처리 후 훈련용 샘플의 수 :',len(train_data))
        
        print('전처리 전 테스트용 샘플의 개수 :',len(test_data))
        test_data.drop_duplicates(subset = ['document'], inplace=True)
        test_data['document'] = test_data['document'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
        test_data['document'] = test_data['document'].str.replace('^ +', "")
        test_data['document'].replace('', np.nan, inplace=True)
        test_data = test_data.dropna(how='any') # Null 값 제거
        print('전처리 후 테스트용 샘플의 개수 :',len(test_data))
        okt = Okt()

        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']

        X_train = []
        for sentence in tqdm(train_data['document']):
            tokenized_sentence = okt.morphs(sentence, stem=True) # 토큰화
            stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stopwords] # 불용어 제거
            X_train.append(stopwords_removed_sentence)

        X_test = []
        for sentence in tqdm(test_data['document']):
            tokenized_sentence = okt.morphs(sentence, stem=True) # 토큰화
            stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stopwords] # 불용어 제거
            X_test.append(stopwords_removed_sentence)
        
        ######################################
        pds = pd.DataFrame(X_train)
        pds.to_csv("sentimental_train_data.csv", mode='w', encoding = 'utf-8-sig', index=False)
        ###############################################
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(X_train)
        
        threshold = 3
        total_cnt = len(tokenizer.word_index) # 단어의 수
        rare_cnt = 0 # 등장 빈도수가 threshold보다 작은 단어의 개수를 카운트
        total_freq = 0 # 훈련 데이터의 전체 단어 빈도수 총 합
        rare_freq = 0 # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

        for key, value in tokenizer.word_counts.items():
            total_freq = total_freq + value

            # 단어의 등장 빈도수가 threshold보다 작으면
            if(value < threshold):
                rare_cnt = rare_cnt + 1
                rare_freq = rare_freq + value

        vocab_size = total_cnt - rare_cnt + 1

    
        tokenizer = Tokenizer(vocab_size) 
        tokenizer.fit_on_texts(X_train)

        X_train = tokenizer.texts_to_sequences(X_train)
        X_test = tokenizer.texts_to_sequences(X_test)

        y_train = np.array(train_data['label'])
        y_test = np.array(test_data['label'])

        drop_train = [index for index, sentence in enumerate(X_train) if len(sentence) < 1]
        drop_test = [index for index, sentence in enumerate(X_test) if len(sentence) < 1]
        
        X_train = np.delete(X_train, drop_train, axis=0)
        y_train = np.delete(y_train, drop_train, axis=0)
        X_test = np.delete(X_test, drop_test, axis=0)
        y_test = np.delete(y_test, drop_test, axis=0)
        
        print('리뷰의 최대 길이 :',max(len(l) for l in X_train))
        print('리뷰의 평균 길이 :',sum(map(len, X_train))/len(X_train))
  
        max_len = 35 ###변경가능
        
        X_train = pad_sequences(X_train, maxlen = max_len)
        X_test = pad_sequences(X_test, maxlen = max_len)

        embedding_dim = 100

        model = Sequential()
        model.add(Embedding(vocab_size, embedding_dim))
        model.add(LSTM(128))
        model.add(Dense(64))
        model.add(Dropout(0.15))
        model.add(Dense(32))
        model.add(Dropout(0.1))
        model.add(Dense(16))
        model.add(Dense(1, activation='sigmoid'))

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)
        mc = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
        history = model.fit(X_train, y_train, epochs=10, callbacks=[es, mc], batch_size=64, validation_split=0.2)

        #loaded_model = load_model('best_model.h5')
        print("\n 테스트 정확도: %.4f" % (model.evaluate(X_test, y_test)[1])) #현재 약 0.84
        

    def sentiment_predict(self, new_sentence):
        okt = Okt()
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
        max_len = 35
        
        #########################
        dfset = pd.read_csv("sentimental_train_data.csv")
        npset = dfset.to_numpy()
        
        dataset = []
        for sentence in npset:
            nan_removed_sentence = [word for word in sentence if str(word) != 'nan'] 
            dataset.append(nan_removed_sentence)
        
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(dataset)
        
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
        
        ##################################
    
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
            
#model_create는 한번만 불러서 모델 저장해두고, 이후에 사용할때는 모델 저장된 path에서, 저장된 모델 불러만 와서 사용하세요! (반복학습X)

model = Model()
model.Model_create()
   
model.sentiment_predict('이 영화 개꿀잼 ㅋㅋㅋ')
#97.73% 확률로 긍정 리뷰입니다.
model.sentiment_predict('어 좋아요. 재난지원금 주세요! 받고 이재명안뽑기')
#70.02% 확률로 부정 리뷰입니다.
model.sentiment_predict('정부의 정책오류와 이상한 오기로 주택가격은 폭등하고 법은누더기됨. 이제와 대출까지막아 사다리끊는 정부를 지지하는 40%는 진짜 실체가있는걸까.. 이제는이재명이 뿌리는 30,40 만원에 넘어갈 국민이 아니라 믿고싶으다..ㅠㅡㅠ')
#60.28% 확률로 부정 리뷰입니다.
model.sentiment_predict('감독 뭐하는 놈이냐?')
#95.01% 확률로 부정 리뷰입니다.
