#install.packages('tidyverse')
#install.packages('rJava')
#install.packages('NLP4kec')
#install.packages('tm')

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
ExNouns <- function(x) {
  require(KoNLP)
  useSejongDic()
  list <- sapply(x, extractNoun, USE.NAMES = FALSE)
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

#빈도표생성함수
Frequency <- function(list) {
  wordcount <- table(unlist(list))
  re_word <- as.data.frame(wordcount, stringsAsFactors = F)
  re_word<-rename(re_word, word = Var1, freq=Freq)
  re_word<-filter(re_word,nchar(word)>=2)                # 두글자 이상 추출
  return(re_word)
}

#clean_data <- Cleaning(file_data)
#nouns <- ExNouns(clean_data)
#df <- Frequency(nouns)


#빈도수가 많은 단어 상위 n개 추출함수
Top_n <- function(df, n) {
  df <- arrange(df, desc(freq))
  top_n <- head(df, n)
  return(top_n)
}

#Top_n(df, 10)  # 빈도수 많은 상위 10개 단어 추출



#####################패키지 설치 시 오류날 때############################
##KoNLP 설치 오류 시
#install.packages("multilinguer")
#library(multilinguer)
#install_jdk()
#install.packages(c('stringr', 'hash', 'tau', 'Sejong', 'RSQLite', 'devtools'), type = "binary")
#install.packages("remotes")
#remotes::install_github('haven-jeon/KoNLP', upgrade = "never", INSTALL_opts=c("--no-multiarch"))
#library(KoNLP) 

##NLP4kec 설치 오류 시
#install.packages("C:/Users/USER/Downloads/NLP4kec_1.4.0.zip", repos = NULL)

##NLP4kec 로드 오류 시 (Error in .jcall(obj, "[Ljava/lang/String;", "rTextParserFromRtoR", .jarray(contentVector).......))
# -> rJava 패키지 문제
#install.packages("rJava")
#source("https://install-github.me/talgalili/installr")
#installr::install.java()

##NLP4kec 설치 후 KoNLP 실행 오류 시(error : stringi 패키지가 없습니다)
#설치되어 있는 stringi 패키지 삭제 후 install.packages('stringi') 입력