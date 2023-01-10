#install.packages('tidyverse')
#install.packages('rJava')
#install.packages('NLP4kec')
#install.packages('lda')
#install.packages('topicmodels')
#install.packages('MASS')
#install.packages('servr')
#install.packages('tm')
#install.packages('mongolite')

setwd('C:/Users/USER/댓글분석/크롤링')
file <- file("movie2_x.txt", encoding = 'EUC-KR')
file_data <- readLines(file)

#전처리함수
Cleaning <- function(x) {
  require(tidyverse)                             # 데이터 전처리(stringr)와 그래프(ggplot2)
  require(rJava)                                 # 아래 NLP4kec 사용을 위해 필요
  require(NLP4kec)                               # 자연어 처리
  require(tm)                                    # 말뭉치 생성, 말뭉치 전처리, DTM 생성
  data <- str_remove_all(x, "[^가-힣A-Za-z]")
  data <- NLP4kec::r_parser_r(contentVector = data, language = 'ko', useEn = TRUE)
  return(data)
}

#명사추출함수
ExNouns <- function(data) {
  require(KoNLP)
  useSejongDic()
  list <- sapply(data, extractNoun, USE.NAMES = FALSE)
  list <- unlist(list)
  list <- str_remove_all(list, "니다")
  list <- str_remove_all(list, "이거")
  list <- str_remove_all(list, "이것")
  list <- str_remove_all(list, "그것")
  list <- str_remove_all(list, "정도")
  list <- str_remove_all(list, "때문")
  list <- str_replace_all(list, "이영화","영화")
  list <- Filter(function(x) { nchar(x) >= 2 && nchar(x) <= 10}, list)
  return(list)
}

# 말뭉치처리함수
Corpus <- function(nouns) {
  require(lda)
  require(stringr)
  corpus <- lexicalize(nouns)
  return(corpus)
}

#LDA 분석에 용이한 format으로 변경해주는 함수
Top_words <- function(n) {
  require(lda)
  require(topicmodels)
  require(MASS)
  require(servr)
  require(stringi)
  set.seed(8000)
  num.iterations <- 6000
  result <- lda.collapsed.gibbs.sampler(corpus$documents,K = 6,corpus$vocab, num.iterations,
                                        0.1, 0.01, compute.log.likelihood = TRUE)
  top.words <- top.topic.words(result$topics, n, by.score = TRUE)
  return(top.words)                                      
}


clean_data <- Cleaning(file_data)
nouns <- ExNouns(clean_data)
corpus <- Corpus(nouns)
Top_15 <- Top_words(15)
Top_15_df <- as.data.frame(Top_15)   
colnames(Top_15_df) <- c('topic1','topic2','topic3','topic4','topic5','topic6')
#Top_15_df

# 결과df를 mongoDB에 저장 
# mongo(collection = '생성할 table명', db = '생성할 database명',.....)
con <- mongolite::mongo(collection = 'topics_R', db = 'test', 
             url = "mongodb://localhost", verbose = TRUE, options = ssl_options())
con$insert(Top_15_df) # 생성한 DB에 결과 df 저장









#####################패키지 설치 시 오류날 때############################
##KoNLP 설치 오류 시
#install.packages("multilinguer")
#library(multilinguer)
#install_jdk()
#install.packages(c('stringr', 'hash', 'tau', 'Sejong', 'RSQLite', 'devtools'), type = "binary")
#install.packages("remotes")
#remotes::install_github('haven-jeon/KoNLP', upgrade = "never", INSTALL_opts=c("--no-multiarch"))


##NLP4kec 설치 오류 시
#install.packages("C:/Users/USER/Downloads/NLP4kec_1.4.0.zip", repos = NULL)


##NLP4kec 로드 오류 시 (Error in .jcall(obj, "[Ljava/lang/String;", "rTextParserFromRtoR", .jarray(contentVector).......))
# -> rJava 패키지 문제
#install.packages("rJava")
#source("https://install-github.me/talgalili/installr")
#installr::install.java()


##NLP4kec 설치 후 KoNLP 실행 오류 시 (error : stringi 패키지가 없습니다)
#설치되어 있는 stringi 패키지 삭제 후 install.packages('stringi') 립력 후 실행
