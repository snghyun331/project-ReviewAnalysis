import os

from flask import Flask, render_template, jsonify, request
import requests
from pymongo import MongoClient
import get_ranking
import shopping
import news
from operator import itemgetter
import word_cloud

app = Flask(__name__)

#client = MongoClient('mongodb://best:scor68@localhost', 27017) #서버에 올릴때, 서버 디비
client = MongoClient('localhost', 27017) #코딩할때 체킹용 디비
db = client.reply



## HTML 화면 보여주기
@app.route('/')
def project_reply():
    return render_template('main.html')

# 뉴스 댓글 분석 결과 창
@app.route('/news_result')
def result01():
    return render_template('news_result.html')

# 상품후기 분석 결과창
@app.route('/shopping_result')
def result02():
    return render_template('shopping_result.html')

# 영화 리뷰 분석 결과창
@app.route('/movie_result')
def result03():
    return render_template('movie_result.html')

@app.route('/api/reply',methods=['GET'])
def number_reply():
    number_news = list(db.number.find({},{'_id':False}))
    return jsonify({'result_count': number_news})

@app.route('/api/issue',methods=['GET'])
def issue_getter():
    issue = get_ranking.get_ranking()
    issue_list = issue.result()

    return jsonify({'hot_issue':issue_list})

# # DB에서 핫토픽을 가져온다
# # (분석할때 마다 토픽 모델링을 통해 토픽을 저장하고 COUNT UP 시킨다.
# # 즉, 토픽에는 {'topic': 이름, 'count': 수} 이렇게 저장되어 있을것!
#
# @app.route('/api/hot_topic',methods = ['GET'])
# def topic_getter():
#     topic_list = db.topic.find({},{'_id':False})
#     new_list = sorted(topic_list,key=itemgetter('count'),reverse=True)
#     return jsonify({'hot_topic':new_list})

# 사용자가 입력한 url을 가져온다.
# 반환은 msg와 classify (숫자) 로 하는데
# msg가 "정상 URL 입니다." 일 때 외에는 classify는 -1을 주고,
# 뉴스일 때 0, 쇼핑몰일 때 1, 영화일 때 2를 반환하도록 한다.
# 그러면 main.html에서는 받은 classify number에 따라 다른 결과 html 파일을 호출한다.
# 이후 논의 후 결정

@app.route('/api/check', methods=['POST'])
def get_url():
    #code = 0 --> "네이버 뉴스, 스마트 스토어, 영화에 대해서만 서비스 합니다."
    #code = 1 --> "정상 URL 입니다."
    #code = 2 --> "요청한 페이지를 찾을 수 없습니다."
    #code = 3 --> "권한이 없어 접근할 수 없습니다."
    #code = 4 --> "웹 서버의 오류로 페이지가 제공되지 않습니다."

    url_recieve = request.form['url_give']  # 입력한 url 받아오기

    # URL VALIDATION CHECK
    valid_url = shopping.naverShopping(url_recieve)
    code = valid_url.Linkcheck()
    classify = -1 #분류 : 유효하지 않은 URL일 경우에는 -1

    # 서비스 가능한 URL일 경우에는 분류코드 (0: 뉴스, 1:스마트스토어, 2: 영화)
    if (code == 1):
        db.url.drop()
        doc = {'url':url_recieve}
        db.url.insert_one(doc)

        #뉴스일 경우
        if ("https://news.naver.com/" in url_recieve):
            classify = 0

        #스마트 스토어인 경우
        elif ("https://smartstore.naver.com/" in url_recieve):
            classify = 1

        # 영화인 경우
        else:
            classify = 2

    # validation code와 분류 코드를 넘겨준다.
    return jsonify({'valid': code,'kind':classify,'url':url_recieve})


@app.route('/api/statics', methods=['GET'])
def give_url():
    url = list(db.url.find({},{'_id':False}))
    url_give = url[0]['url']
    desc = news.naverNews(url_give)
    doc = desc.get_des()

    return jsonify(doc)

@app.route('/api/contention', methods=['GET'])

def give_contention():
    file = './static/assets/wordcloud.png'

    if os.path.isfile(file):
        os.remove(file)

    url_give = list(db.url.find({},{'_id':False}))
    url = url_give[0]['url']
    reply = news.naverNews(url)
    # clean bot이 작동하고 있는 경우
    reply_list = reply.clean_bot_reply()
    title = reply.get_title()
    new_list = sorted(reply_list, key=itemgetter('논란수치'), reverse=True)[0:10]
    num = len(reply_list)
    time=[]

    #작성시간 분포도는 년월일시 별로 분포도를 그리도록한다. (분까지 원할경우 real_date에 hms[1]을 넣어주면 된다.
    for l in reply_list:
        tmp = l['작성시간']
        tmp = tmp[1:-6]
        tmp1 = tmp.split('T')
        date = tmp1[0].split('-')
        hms = tmp1[1].split(':')
        real_date = date[0]+date[1]+date[2]+hms[0]
        time.append(real_date)

    time_give={}
    for t in time:
        try:time_give[t] +=1
        except:time_give[t] = 1
    time_give = sorted(time_give.items())

    tmp = ""
    for l in reply_list:
        tmp += l['댓글내용'][1:-1]
        tmp += " "

    cloud = word_cloud.wordcloud(tmp)
    cloud.make_cloud_image("wordcloud")

    db.text.drop()
    doc = {'text': tmp}
    db.text.insert_one(doc)

    return jsonify({'contention_reply':new_list,'number':num,'title':title,'url':url,'time':time_give})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
