pkg_fun <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
    library(pkg, character.only = TRUE)
  }
}

Sys.setlocale("LC_CTYPE", ".1251")

# 1. 기본 전처리 ; 명사추출
pkg_fun("readr")
pkg_fun("dplyr")
pkg_fun("stringr")
pkg_fun("textclean")
pkg_fun("mongolite")
pkg_fun("tidytext")
pkg_fun("tm")
pkg_fun("topicmodels")
pkg_fun("reshape2")

newdb <- mongo(collection = "nouns",
               db = "reply",
               url = "mongodb://localhost",
               verbose = TRUE)
test <- newdb$find()

#id 부여
row <-nrow(test)
id <- 1:row
test <- cbind(id,test) %>% filter(str_count(word)>1)


#개수 세기
count_word <- test %>% add_count(word) %>% add_count(n <= 200) %>% select(-n)

# 4. LDA 모델 생성
count_word_doc <- count_word %>% count(word,sort=T)

#dtm 생성
row <- nrow(count_word_doc)
id <- 1:row
count_word_doc <- cbind(id,count_word_doc)
dtm_comment <- count_word_doc %>% cast_dtm(document=id,term = word, value=n)

#LDA 모델 생성
LDA_models <- LDA(dtm_comment,k=5,method="Gibbs",control=list(seed= 1234))

#beta 추출 및 각 토픽 별 상위 5개의 단어 추출

term_topic <- tidy(LDA_models,matrix="beta")
# term_topic <- terms(LDA_models,20) %>% data.frame()
top_term_topic <- term_topic %>% group_by(topic) %>% slice_max(beta,n=5,with_ties = F)

#list를 dataframe으로 변환
result <- as.data.frame(top_term_topic)

#db에 저장
con <- mongo(collection = "topicModeling",
               db = "reply",
               url = "mongodb://localhost",
               verbose = TRUE)

if(con$count() > 0) con$drop()
con$insert(result)