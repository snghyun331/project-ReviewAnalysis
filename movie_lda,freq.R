setwd('C:/Users/USER/댓글분석/크롤링')
file <- file("new_no_spolier.txt", encoding = 'EUC-KR')   # 파일형식: 댓글 하나당 한줄씩
file_data <- readLines(file) 

library(stringr)
library(tidyverse)
library(KoNLP)
library(tm)
useSejongDic()

file_data <- str_replace_all(file_data, pattern = "/r", replacement = "")
file_data <- str_remove_all(file_data, '영화')
file_data <- str_remove_all(file_data, '근데')
file_data <- str_remove_all(file_data, '하나')
file_data <- str_remove_all(file_data, '그리고')
file_data <- str_remove_all(file_data, '정도')
file_data <- str_remove_all(file_data, '이것')
file_data <- str_remove_all(file_data, '너무')
file_data <- str_remove_all(file_data, '진짜')
file_data <- str_remove_all(file_data, '본거')
file_data <- str_remove_all(file_data, '그거')

ko_words <- function(doc) {
  pos <- str_split(doc, ";")
  pos <- paste(SimplePos22(pos))
  extracted <- str_match(pos, "([가-힣a-zA-Z]+)/[NC]")
  
  keyword <- extracted[,2]
  keyword[!is.na(keyword)]
}

options(mc.cores = 1)
myCorpus <- VCorpus(VectorSource(file_data))
tour_tdm <- TermDocumentMatrix(myCorpus, control = list(tokenize = ko_words,
                                                        removePunctuation = T, removeNumbers = T,
                                                        wordLengths = c(2,10)))

## 빈도수 계산
wordFreq <- slam::row_sums(tour_tdm)
wordFreq <- sort(wordFreq, decreasing = T)
df <- as.data.frame(wordFreq)
df


## LDA
dtm <- as.DocumentTermMatrix(tour_tdm)
rowTotals <- apply(dtm, 1, sum)
dtm.new <- dtm[rowTotals > 0, ]
dtm <- dtm.new

library(topicmodels)
lda <- LDA(dtm, k=4, control = list(seed = 10000))  # 4개토픽
term <- terms(lda, 10)  # 한 토픽당 10개 단어 추출
df <- as.data.frame(term)
df
