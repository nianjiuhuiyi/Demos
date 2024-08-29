import pandas as pd
import numpy as np
import jieba.posseg
import jieba.analyse
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import pprint

#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
#设置value的显示长度为100，默认为50
pd.set_option('max_colwidth',100)

"""
       TF-IDF权重：
           1、CountVectorizer 构建词频矩阵(是把所有的评论文本在一起做的词频统计)
           2、TfidfTransformer 构建tfidf权值计算
           3、文本的关键字
           4、对应的tfidf矩阵
"""


# 数据预处理操作：分词，去停用词，词性筛选
def dataPrepos(text, stopkey):
    words = []
    pos = ['n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd']  # 定义选取的词性
    seg = jieba.posseg.cut(text)  # 分词
    for i in seg:
        if i.word not in stopkey and i.flag in pos:  # 去停用词 + 词性筛选
            words.append(i.word)
    return words


# tf-idf获取文本top10关键词
def getKeywords_tfidf(data, stopkey, topK):
    idList, titleList, abstractList = data['id'], data['title'], data['content']
    corpus = []  # 将所有文档输出到一个list中，一行就是一个文档
    for index in range(len(idList)):
        text = titleList[index] + ': ' + abstractList[index]  # 拼接标题和摘要
        text = dataPrepos(text, stopkey)  # 文本预处理
        text = " ".join(text)
        corpus.append(text)
    # 1、构建词频矩阵，将文本中的词语转换成词频矩阵
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)  # 词频矩阵,a[i][j]:表示j词在第i个文本中的词频
    # 2、统计每个词的tf-idf权值
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    # 3、获取词袋模型中的关键词
    word = vectorizer.get_feature_names()
    # 4、获取tf-idf矩阵，a[i][j]表示j词在i篇文本中的tf-idf权重
    weight = tfidf.toarray()
    # 5、打印词语权重
    ids, titles, keys = [], [], []
    for i in range(len(weight)):
        ids.append(idList[i])
        titles.append(titleList[i])

        df_word = word     # 所有文章的所有word
        df_weight = weight[i].tolist()  # 当前文章的所有词与总词汇表的权重列表，长度是与上面的df_word长度一样
        word_weight = list(zip(df_word, df_weight))
        word_weight.sort(key=lambda x: x[1], reverse=True)  # 按照权重排序
        temp = filter(lambda x: x[0] in corpus[i], word_weight)   # word 必须要在这个文档中才保留
        key_word = [a_word[0] for a_word in temp]
        word_split = " ".join(key_word)
        keys.append(word_split)

    result = pd.DataFrame({"id": ids, "title": titles, "key": keys}, columns=['id', 'title', 'key'])
    return result


def main():
    # 读取数据集
    # dataFile = './data/sample_data.csv'
    dataFile = 'data/comment.csv'
    data = pd.read_csv(dataFile, encoding='gbk')
    print(data.head())
    # 停用词表
    stopkey = [w.strip() for w in open('data/stopWord.txt', 'r', encoding='utf-8').readlines()]
    # tf-idf关键词抽取
    result = getKeywords_tfidf(data, stopkey, 10)
    # result.to_csv("result/keys_comment_TFIDF.csv", index=False)
    print(result)

if __name__ == '__main__':
    main()
