# coding=utf-8

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)
np.random.seed(0)

# 将DataFrame格式转成dict格式，同时丢到Nan的数据
def dataframe2dict(dataframe):
    """
    将pandas的DataFrame转成字典like this --> {index0:{columns0:3, columns1:5...}, ...}
    当value为nan时就忽略
    :param dataframe: pandas的DataFrame格式数据
    :return:
    """
    out = {}
    for userName, courses_rate in dataframe.to_dict("index").items():
        for courseName, rating in courses_rate.items():
            if rating > 0:  # 值都大于0，为了丢掉nan
                out.setdefault(userName, {})
                out[userName][courseName] = rating
    return out


class LFM():

    def __init__(self, rating_data, k, alpha=0.1, lmbd=0.1, max_iter=500):
        self.k = k
        self.user = dict()
        self.item = dict()
        self.alpha = alpha
        self.lmbd= lmbd
        self.max_iter = max_iter
        self.rating_data = rating_data

        """随机初始化矩阵user、item
        rating_data(m*n) -->   user(m*k) * item(k*n)
        """
        for username, rates in self.rating_data.items():
            self.user[username] = [np.random.random() / np.sqrt(self.k) for _ in range(self.k)]
            for itemname in rates:
                if itemname not in self.item:
                    self.item[itemname] = [np.random.random() / np.sqrt(self.k) for _ in range(self.k)]

    def train(self):
        loss = 0
        losses = []
        for step in range(self.max_iter):
            for username, rates in self.rating_data.items():
                for itemname, rate in rates.items():
                    pre_score = self.predict(username, itemname)
                    loss = rate - pre_score

                    a = np.array(self.user[username])
                    b = np.array(self.item[itemname])
                    self.user[username] = a + self.alpha * (loss * b - self.lmbd * a)
                    self.item[itemname] = b + self.alpha * (loss * a - self.lmbd * b)

            if step % 10 == 0:
                print("{}/{} loss:{}".format(step, self.max_iter, loss))
            plt.clf()
            plt.plot(losses)
            plt.pause(0.1)

            self.alpha *= 0.9    # 每次迭代步长逐步缩小
            losses.append(loss)

            # 当本次loss与上次loss只差小于0.0001时就不再训练
            if len(losses) > 2 and (losses[-2] - losses[-1] < 0.0001):   # 当本次loss与上次loss只差小于0.0001时就不再训练
                break

    def predict(self, username, itemname):
        score = np.dot(np.mat(self.user[username]), np.mat(self.item[itemname]).T)
        return score.item()


def recommend(username, n):
    """
    但实际上MF学出来的每一维不一定都能有这么好的解释，很多时候甚至可能都无法直观地解释每一维，但每一维的确又代表了一个类别，
    因此我们把这种类别称为隐类别，把用户向量和歌曲向量中的每一维称为隐变量。所以矩阵分解是一种隐变量模型。
    隐类别的个数是要我们事先指定的，也就是上面的那个k，k 越大，隐类别就分得越细，计算量也越大。
    """
    dataframe = pd.read_csv("person_course_rate.csv", index_col=0)
    dataframe = dataframe.iloc[:10, :100]  # 数据太多，先取一部分来看效果
    ratings = dataframe2dict(dataframe)
    lfm = LFM(ratings, k=5)   # k是超参数，例如把n个歌名分成了(民谣、摇滚、rap)，那k就是3；
    lfm.train()
    # print(lfm.predict("窦一笑", "明细:2.5 空调系统.1"))    # 这个本来有值，是1.649688
    # print(lfm.predict("窦一笑", "明细:1.1 岗位安全生产规章制度"))    # 这个本来的值是Nan，现在得到的就是预测的值
    # print(lfm.item["明细:1.1 岗位安全生产规章制度"])

    temp = pd.isna(dataframe.loc[username])   # 没有评分的课程
    nan_keys = dataframe.loc[username, temp].index   # 获取到了没有评价的课程的名称
    nan_values = [(key, lfm.item[key]) for key in nan_keys if key in lfm.item]  # 必须加这个判断，
    # 得到的是共同的，但是这人没评价的课程的向量值，shape一般是（a, k）a:任意的数字(有几就是几个课程)、k：上面的超参数k
    # 10个人，100个课，可能其中有几十个课都没人评价，那么这个方法是保证每个课都至少有一个人评价了才行，如果一个课没人评价是训练不了的

    nan_values = np.asarray(nan_values)
    temp = np.array([nan_values[i, 1] for i in range(nan_values.shape[0])])  # 将列表值取出获得ndarray格式，方便后续矩阵运算
    nan_values[:, 1] = np.dot(np.array(lfm.user[username]), temp.T)   # 对应的就是课程及其预测打分
    # lfm.user["窦一笑"] -->shape=(1, k)  k:上面的超参， 这个值就是先随机初始化的人员矩阵经过训练后的人员值
    index = (-nan_values[:, 1]).argsort()  # 按预测score从高到低排序
    results = nan_values[index]
    return results[:n, 0].tolist()    # 推荐前n个课程名称


if __name__ == '__main__':
    recom_list = recommend("窦一笑", 5)
    print("推荐的课程有:{}".format(recom_list))
