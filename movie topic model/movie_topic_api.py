from flask import Flask, jsonify
from pymongo import MongoClient

# api 생성
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False    # 한글 깨짐 방지

# db 불러오기 ( 제 기준 db)
client = MongoClient('localhost', 27017)
db = client['test']   # database 불러오기
table = db['topics_R']   # database 안의 table 불러오기

@app.route('/movie', methods=['GET'])
def topic_model():
    lists = []
    for y in list(table.find({}, {'_id': False})):
        lists.append(y)
    return jsonify(lists)

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)


