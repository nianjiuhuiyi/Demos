from LAC import LAC
import pandas as pd
import pprint
import jieba
import jieba.posseg

def dataPrepos(text, stopkey):
    words = []
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd']  # 定义选取的词性
    seg = jieba.posseg.cut(text)  # 分词
    for i in seg:
        if i.word not in stopkey and i.flag in pos:  # 去停用词 + 词性筛选
            words.append(i.word)
    return words

lac = LAC(mode='seg')
data = pd.read_csv('./keyextract/data/comment.csv', encoding='gbk')
text = data['content'].values
out = lac.run(text.tolist())
pprint.pprint(out)


def main():
    data = pd.read_csv('./keyextract/data/comment.csv', encoding='gbk')
    # 停用词表
    stopkey = [w.strip() for w in open('./keyextract/data/stopWord.txt', encoding='utf-8').readlines()]
    texts = data['content'].values.tolist()
    for text in range(len(texts)):
        text = dataPrepos(text, stopkey)
        print(text)
        exit()


if __name__ == '__main__':
    main()

