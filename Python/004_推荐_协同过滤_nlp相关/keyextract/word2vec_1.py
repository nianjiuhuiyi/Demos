# 采用Word2Vec词聚类方法抽取关键词1——获取文本词向量表示
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')  # 忽略警告
import pandas as pd
import time
import numpy as np
import jieba
import jieba.posseg
import gensim


# 返回特征词向量
def getWordVecs(wordList, model):
    name = []
    vecs = []
    for word in wordList:
        word = word.replace('\n', '')
        try:
            if word in model:
                # name.append(word.encode('utf8'))
                name.append(word)
                vecs.append(model[word])
        except KeyError:
            continue
    a = pd.DataFrame(name, columns=['word'])
    b = pd.DataFrame(np.array(vecs, dtype='float'))
    return pd.concat([a, b], axis=1)


# 数据预处理操作：分词，去停用词，词性筛选
def dataPrepos(text, stopkey):
    words = []
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd']  # 定义选取的词性
    seg = jieba.posseg.cut(text)  # 分词
    for i in seg:
        if i.word not in words and i.word not in stopkey and i.flag in pos:  # 去重 + 去停用词 + 词性筛选
            words.append(i.word)
    return words


# 根据数据获取候选关键词词向量
def buildAllWordsVecs(data, stopkey, model):
    idList, titleList, abstractList = data['id'], data['title'], data['content']
    for index in range(len(idList)):
        id = idList[index]
        title = titleList[index]
        abstract = abstractList[index]
        l_ti = dataPrepos(title, stopkey)  # 处理标题
        l_ab = dataPrepos(abstract, stopkey)
        # 获取候选关键词的词向量
        words = np.append(l_ti, l_ab)
        words = list(set(words))  # 数组元素去重,得到候选关键词列表
        wordvecs = getWordVecs(words, model)  # 获取候选关键词的词向量表示
        # 词向量写入csv文件，每个词400维
        data_vecs = pd.DataFrame(wordvecs)
        print(wordvecs)
        data_vecs.to_csv('result/vecs/wordvecs_' + str(id) + '.csv', index=False)


def main():
    dataFile = 'data/comment.csv'
    data = pd.read_csv(dataFile, encoding='gbk')
    # 停用词表
    stopkey = [w.strip() for w in open('data/stopWord.txt', encoding='utf-8').readlines()]
    # 词向量模型
    begin = time.time()
    model = gensim.models.KeyedVectors.load_word2vec_format('data/wiki.zh.text.vector', binary=False)
    end = time.time()
    print('加载模型用时:{:.2f}min'.format((end - begin) / 60))
    buildAllWordsVecs(data, stopkey, model)


if __name__ == '__main__':
    main()
