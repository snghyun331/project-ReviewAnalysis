from flask import Flask, jsonify
from pymongo import MongoClient
import not_spolier
import spolier

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.reply

# 기술통계(네티즌 평점, 문장, 성별/나이 관람비율, 성별/나이 만족도, 감상포인트
@app.route('/api/statics', methods=['GET'])
def give_url():
    url = list(db.url.find({},{'_id':False}))
    url_give = url[0]['url']
    statics_url = not_spolier.movie(url_give)        # statics = spolier.movie(url_give)
    doc = statics_url.get_statics()
    return jsonify(doc)


# 댓글의 평점, 날짜, 댓글, 공감, 비공감
@app.route('/api/comment', methods = ['GET'])
def give_review():
    url = list(db.url.find({},{'_id' : False}))
    url_give = url[0]['url']
    review_url = not_spolier.movie(url_give)          # review_url = spolier.movie(url_give)
    review_list = review_url.reviews()

    # 댓글작성시간분포
    time = []
    for i in review_list:
        date = i['날짜']
        date = date.split('.')
        real_date = date[0] + date[1] + date[2]
        time.append(real_date)

    time_give = {}
    for t in time:
        try:
            time_give[t] += 1
        except:
            time_give[t] = 1
    time_give = sorted(time_give.items())

    return jsonify({'reply':review_list, 'time':time_give})


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)