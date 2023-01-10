#install.packages(c("DBI","RSQLite"))
library(DBI)
library(RSQLite)
library(plyr)
library(stringr)

setwd("c:/Users/rlaek/bedat_txt")

txt<-readLines("bedet_news.txt",encoding="UTF-8")
txt=txt[-1]

positive<-readLines("positive.txt",encoding="UTF-8")
positive=positive[-1]

negative<-readLines("negative.txt",encoding="UTF-8")
negative=negative[-1]

#print(txt)
#print(positive)
#print(negative)

sentimental = function(sentences, positive, negative){
  
  scores = laply(sentences, function(sentence, positive, negative) {
    
    sentence = gsub('[[:punct:]]', '', sentence) # 문장부호 제거
    sentence = gsub('[[:cntrl:]]', '', sentence) # 특수문자 제거
    sentence = gsub('\\d+', '', sentence)        # 숫자 제거
    
    word.list = str_split(sentence, '\\s+')      # 공백 기준으로 단어 생성 -> \\s+ : 공백 정규식, +(1개 이상)
    words = unlist(word.list)                    # unlist() : list를 vector 객체로 구조변경
    
    pos.matches = match(words, positive)           # words의 단어를 positive에서 matching
    neg.matches = match(words, negative)
    
    pos.matches = !is.na(pos.matches)            # NA 제거, 위치(숫자)만 추출
    neg.matches = !is.na(neg.matches)
    
    score = sum(pos.matches) - sum(neg.matches)  # 긍정 - 부정   
    return(score)
  }, positive, negative)
  
  scores.df = data.frame(score=scores, text=sentences)
  return(scores.df)

}

result=sentimental(txt, positive, negative)

result$color[result$score >=1] = "blue"
result$color[result$score ==0] = "green"
result$color[result$score < 0] = "red"

print(table(result$color))

result$remark[result$score >=1] = "긍정"
result$remark[result$score ==0] = "중립"
result$remark[result$score < 0] = "부정"

sentiment_result= table(result$remark)

pie(sentiment_result, main="감성분석 결과",
    col=c("blue","red","green"), radius=0.8)

print(result)

#blue green   red 
#40   260    53 



