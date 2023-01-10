from konlpy.tag import Okt
from pymongo import MongoClient
from collections import Counter

stop_words = ['절대','그냥','너희','이번','다음','지금','누가','퍼트','현재',"니들","풀어주","절대","너희들","안하","단지","어차피","걔네","하다","하게","들이","만큼","이것",
"아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의",
"가", "으로", "로", "에게", "뿐이다" ,"의거하여", "근거하여", "입각하여", "기준으로", "예하면", "예를", "들면", "들자면" ,"저",
"소인" ,"소생", "저희", "지말고", "하지마", "하지마라", "다른", "물론", "또한", "그리고", "비길수" ,"없다",
"해서는", "안된다", "뿐만", "아니라", "만이", "아니다", "만은", "아니다", "막론하고", "관계없이",
"그치지", "않다", "그러나", "그런데", "하지만", "든간에", "논하지", "않다", "따지지", "설사" ,"비록" ,"더라도",
"아니면" ,"만", "못하다", "하는", "편이", "낫다", "불문하고", "향하여", "향해서" ,"향하다", "쪽으로", "틈타", "이용하여",
"타다", "오르다", "제외하고", "외에", "밖에", "하여야", "비로소", "한다면", "몰라도", "외에도", "이곳", "여기",
"부터", "기점으로", "따라서", "할", "생각이다", "하려고하다", "이리하여", "그리하여", "그렇게", "함으로써", "하지만",
"일때", "할때", "앞에서", "중에서", "보는데서", "으로써", "로써", "까지", "해야한다", "일것이다", "반드시",
"할줄알다" ,"할수있다", "할수있어", "임에", "틀림없다", "한다면", "등", "등등", "제", "겨우", "단지", "다만", "할뿐",
"딩동", "댕그", "대해서", "대하여", "대하면", "훨씬", "얼마나", "얼마만큼", "얼마큼", "남짓", "여", "얼마간",
"약간", "다소", "좀", "조금", "다수", "몇", "얼마", "지만" ,"하물며", "또한", "그러나", "그렇지만", "하지만", "이외에도", "대해",
"말하자면", "뿐이다", "다음에", "반대로" ,"말하자면" ,"이와", "바꾸어서" ,"말하면", "한다면", "만약" ,"그렇지않으면",
"까악", "삐걱거리다", "보드득", "비걱거리다", "꽈당", "응당", "해야한다", "에", "가서", "각각", "여러분",
"각종", "각자", "제각기", "하도록하다", "그러므로", "그래서", "고로" ,"한", "까닭에", "하기", "때문에", "거니와",
"이지만", "대하여", "관하여", "관한", "과연", "실로", "아니나다를가", "생각한대로", "진짜로", "한적이있다",
"하곤하였다", "하하", "허허", "아하", "거바", "왜", "어째서", "무엇때문에", "어찌", "하겠는가", "무슨", "어디",
"어느곳", "더군다나", "하물며", "더욱이는", "어느때", "언제", "이봐", "어이", "여보시오", "흐흐","헉헉",
"헐떡헐떡", "영차", "여차", "어기여차", "끙끙" ,"아야","콸콸", "졸졸", "좍좍", "뚝뚝", "주룩주룩", "솨",
"우르르", "그래도", "또", "그리고", "바꾸어말하면", "바꾸어말하자면", "혹은", "혹시", "답다", "및",
"그에", "따르는", "때가", "되어", "즉", "지든지", "설령", "가령", "하더라도", "할지라도", "일지라도",
"지든지", "몇", "거의", "하마터면", "인젠", "이젠", "된바에야", "된이상", "만큼", "어찌됏든",
"그위에", "게다가", "점에서", "보아", "비추어", "보아", "고려하면", "하게될것이다", "일것이다", "비교적", "좀" ,"보다더", "비하면", "시키다", "하게하다",
"할만하다", "의해서", "연이서", "이어서", "잇따라", "뒤따라", "뒤이어", "결국", "의지하여", "기대여", "통하여", "자마자", "더욱더", "불구하고", "얼마든지", "마음대로"
,"당연","당신","얼마","살았","하시","고통스럽","^ㅋ","ㅋㅋ","ㅋㅋㅋ","^ㅎ","ㅎㅎ","내년","어쩌","가즈","드러븐","정도","수가","이전"]
class Analysis_noun:
    def __init__(self,text):
        self.text = text

    def extractNoun(self):
        okt = Okt()
        morph = okt.pos(self.text)

        noun = []
        for word, tag in morph:
            if tag in ['Noun'] and word not in stop_words:
                noun.append(word)

        for i,v in enumerate(noun):
            if v in stop_words:
                noun.pop(i)
        noun = [n for n in noun if len(n)>1]

        return noun

    def noun_counter(self):
        noun = self.extractNoun()
        count = Counter(noun)
        return count

    def top10(self):
        count = self.noun_counter()
        top10=count.most_common(n=10)
        print(len(top10))
        list = []
        for i in range(len(top10)):
            tmp = {}
            tmp['noun'] = top10[i][0]
            tmp['n'] = top10[i][1]
            list.append(tmp)
        return list

class Analysis_Ad:
    def __init__(self,text):
        self.text = text

    def extractAd(self):
        nlpy = Okt()

        # 각 문장별로 형태소 구분하기
        sentences_tag = []
        for sentence in self.text:

            morph = nlpy.pos(sentence,stem=True)
            sentences_tag.append(morph)

        # 명사 or 형용사인 품사만 선별해 리스트에 담기
        noun_adj_list = []
        for sentence in sentences_tag:
            for word, tag in sentence:
                if tag in ['Adjective','Noun'] and word not in ['아주', '정말', '모두', '진짜', '완전']:
                    noun_adj_list.append(word)


        return noun_adj_list

    def extractOnlyAd(self):
        nlpy = Okt()
        # 각 문장별로 형태소 구분하기
        sentences_tag = []
        for sentence in self.text:
            # sentence = nlpy.normalize(sentence)
            morph = nlpy.pos(sentence, stem=True)
            sentences_tag.append(morph)

        # 명사 or 형용사인 품사만 선별해 리스트에 담기
        adj_list = []
        for sentence in sentences_tag:
            for word, tag in sentence:
                if tag in ['Adjective'] and word not in ['아주', '정말', '모두', '진짜', '완전','있다','아니다','어떻다','이렇다','그렇다','같다','없다']:
                    adj_list.append(word)
        return adj_list

    def ad_counter(self):
        words = self.extractAd()
        count = Counter(words)
        return count

    def only_ad_counter(self):
        words = self.extractOnlyAd()
        count = Counter(words)
        return count

    def top10(self):
        count = self.only_ad_counter()
        top10=count.most_common(n=3)
        print(len(top10))
        list = []
        for i in range(len(top10)):
            tmp = {}
            tmp['noun'] = top10[i][0]
            tmp['n'] = top10[i][1]
            list.append(tmp)
        return list


# if __name__ == '__main__':
#     client = MongoClient('localhost', 27017)  # 코딩할때 체킹용 디비
#     db = client.reply
#     text = list(db.text.find({}, {'_id': False}))
#     text = text[0]['text']
#
#     analysis = Analysis_Ad(text)
#     print(analysis.ad_counter())
