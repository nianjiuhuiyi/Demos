# 采用Word2Vec词聚类方法抽取关键词2——根据候选关键词的词向量进行聚类分析
import os
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import math


# 对词向量采用K-means聚类抽取TopK关键词
def getkeywords_kmeans(data, topK):
    words = data["word"]
    vecs = data.iloc[:, 1:]  # 向量
    kmeans = KMeans(n_clusters=1, random_state=10).fit(vecs)
    labels = kmeans.labels_
    labels = pd.DataFrame(labels, columns=['label'])
    vec_center = kmeans.cluster_centers_  # 聚类中心

    # 计算欧式距离（相似性）
    distances = []
    vec_words = np.array(vecs)
    vec_center = vec_center[0]
    length = len(vec_center)
    for index in range(len(vec_words)):
        cur_wordvec = vec_words[index]  # 当前词语的词向量
        dis = 0  # 向量距离
        for index2 in range(length):
            dis += (vec_center[index2] - cur_wordvec[index2]) * (vec_center[index2] - cur_wordvec[index2])
        dis = math.sqrt(dis)
        distances.append(dis)
    distances = pd.DataFrame(distances, columns=['dis'])

    result = pd.concat([words, labels, distances], axis=1)  # 拼接词语与其对应中心点的距离
    result = result.sort_values(by="dis", ascending=True)  # 按照距离大小进行升序排序

    # 抽取排名前topK个词语作为文本关键词
    wordlist = np.array(result['word'])
    word_split = [wordlist[x] for x in range(0, topK)]  # 抽取前topK个词汇
    word_split = " ".join(word_split)
    return word_split


def main():
    dataFile = 'data/comment.csv'
    articleData = pd.read_csv(dataFile, encoding="gbk")
    ids, titles, keys = [], [], []
    rootdir = "result/vecs"  # 词向量文件根目录
    fileList = os.listdir(rootdir)

    for i in range(len(fileList)):
        filename = fileList[i]
        path = os.path.join(rootdir, filename)
        if os.path.isfile(path):
            data = pd.read_csv(path, encoding='utf-8')
            artile_keys = getkeywords_kmeans(data, 10)  # 聚类算法得到当前文件的关键词
            # 根据文件名获得文章id以及标题
            (shortname, extension) = os.path.splitext(filename)  # 得到文件名和文件扩展名
            t = shortname.split("_")
            article_id = int(t[len(t) - 1])
            artile_tit = articleData[articleData.id == article_id]['title']  # 获得文章标题
            artile_tit = list(artile_tit)[0]  # series转成字符串
            ids.append(article_id)
            titles.append(artile_tit)
            keys.append(artile_keys)
    # 所有结果写入文件
    result = pd.DataFrame({"id": ids, "title": titles, "key": keys}, columns=['id', 'title', 'key'])
    result = result.sort_values(by="id", ascending=True)
    result.to_csv("result/keys_word2vec.csv", index=False)


if __name__ == '__main__':
    main()
