
import json
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

def solution_model():
    with open('words.json', 'r') as f:
        datastore = json.load(f)

    vocab_size = 1000
    embedding_dim = 16
    max_length = 120
    trunc_type='post'
    padding_type='post'
    oov_tok = "<OOV>"
    training_size = 20000

    sentences = []
    labels = []
    
    #1. 데이터

    for item in datastore:
        sentences.append(item['headline'])
        labels.append(item['is_Positive'])

    training_sentenses = sentences[0:training_size]
    test_sentenses = sentences[training_size:]
    training_labels = labels[0:training_size]
    test_labels = labels[training_size:]

    print(training_sentenses[0])
    print(training_labels[0])
    print(training_sentenses[1111])
    print(training_labels[1111])

    # 넘파이로 변경
    training_sentenses = np.array(training_sentenses)
    test_sentenses = np.array(test_sentenses)
    training_labels = np.array(training_labels)
    test_labels = np.array(test_labels)

    # 토크나이저
    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
    tokenizer.fit_on_texts(training_sentenses)

    word_index = tokenizer.word_index
    print(word_index)

    training_sequences = tokenizer.texts_to_sequences(training_sentenses)
    print(training_sequences)
    training_padded = pad_sequences(training_sequences, maxlen=max_length,
                                    padding=padding_type, truncating=trunc_type)

    test_sequences = tokenizer.texts_to_sequences(test_sentenses)
    test_padded = pad_sequences(test_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)

    #2. 모델구성
    model = tf.keras.Sequential([
    # YOUR CODE HERE. KEEP THIS OUTPUT LAYER INTACT OR TESTS MAY FAIL
        tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
        tf.keras.layers.LSTM(64, return_sequences=True, activation='relu'),
        tf.keras.layers.LSTM(64, return_sequences=True, activation='relu'),
        tf.keras.layers.Conv1D(64, 2, activation='relu'),
        tf.keras.layers.GlobalMaxPool1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])


    #3. 컴파일, 훈련
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])

    model.fit(training_padded, training_labels, epochs=20,
              validation_data=(test_padded, test_labels), verbose=1)

    return model
    
if __name__ == '__main__':
    model = solution_model()
    model.save("mymodel.h5")
