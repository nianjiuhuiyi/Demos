# -*- coding: cp936 -*-
import numpy as np
import tqdm
import pprint

# 一个字典，第一个key是人名，value是又是一个字典，字典里面是key电影名，value是评分
critics = {
    'LisaRose': {
        'LadyintheWater': 2.5,
        'SnakesonaPlane': 3.5,
        'JustMyLuck': 3.0,
        'SupermanReturns': 3.5,
        'You,MeandDupree': 2.5,
        'TheNightListener': 3.0},
    'GeneSeymour': {
        'LadyintheWater': 3.0,
        'SnakesonaPlane': 3.5,
        'JustMyLuck': 1.5,
        'SupermanReturns': 5.0,
        'TheNightListener': 3.0,
        'You,MeandDupree': 3.5},
    'MichaelPhillips': {
        'LadyintheWater': 2.5,
        'SnakesonaPlane': 3.0,
        'SupermanReturns': 3.5,
        'TheNightListener': 4.0},
    'ClaudiaPuig': {
        'SnakesonaPlane': 3.5,
        'JustMyLuck': 3.0,
        'TheNightListener': 4.5,
        'SupermanReturns': 4.0,
        'You,MeandDupree': 2.5},
    'MickLaSalle': {
        'LadyintheWater': 3.0,
        'SnakesonaPlane': 4.0,
        'JustMyLuck': 2.0,
        'SupermanReturns': 3.0,
        'TheNightListener': 3.0,
        'You,MeandDupree': 2.0},
    'JackMatthews': {
        'LadyintheWater': 3.0,
        'SnakesonaPlane': 4.0,
        'TheNightListener': 3.0,
        'SupermanReturns': 5.0,
        'You,MeandDupree': 3.5}}



def sim_distance(prefs, person1, person2):
    """
    利用欧几里得计算两个人之间的相似度(在有共同电影评分你的情况下)
    :param prefs:不同人对多部电影的评分字典
    :param person1:任意一人姓名
    :param person2:任意一人姓名
    :return: 结果把欧式距离转换一下，距离越小，相似度越大，值在(0,1]之间
    """
    # 首先把这个两个用户共同拥有评过分电影给找出来，方法是建立一个字典，字典的key是电影名字，电影的值就是1
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    # 如果没有共同之处
    if len(si) == 0:
        return 0
    # 计算所有有相同电影评分的的平方和
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in si])
    return 1 / (1 + np.sqrt(sum_of_squares))
# print(sim_distance(critics, "JackMatthews", "MickLaSalle"))


def sim_pearson(prefs, p1, p2):
    """
    计算两个人的皮尔逊相关系数,一般用于计算两个定距变量间联系的紧密程度，取值在[-1, 1]之间
    :param prefs:同人对多部电影的评分字典
    :return:
    """
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    # 如果两者没有共同之处，则返回0
    n = len(si)
    if n == 0:
        return 0
    # 对共同拥有的物品的评分，分别求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    # 求平方和
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    # 求乘积之和
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    # 计算皮尔逊评价值
    num = pSum - (sum1 * sum2 / len(si))
    den = np.sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    return num / den
# print(sim_pearson(critics, "JackMatthews", "MickLaSalle"))


def tanimoto(a, b):
    """
    Tanimoto系数(就是两个集合的交集/两个集合的并集),相当于cosine的扩展，也多用于计算文档数据的相似度
    """
    c = [v for v in a if v in b]
    return float(len(c)) / (len(a) + len(b) - len(c))


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """
    针对一个目标用户，返回和其相似度高的人
    :param prefs: 不同人对多部电影的评分字典
    :param person: 具体需要推荐业务的人的名字
    :param n:默认前5个
    :param similarity: 相似度计算的方法，默认用的皮尔逊相似度
    :return:返回长度为n的，与person相似度最高的n个人的列表
    """
    scores = [(other, similarity(prefs, person, other)) for other in prefs if other != person]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]
# print(topMatches(critics, "JackMatthews"))


""""

    
    :param prefs:
    :param person:
    :param similarity:
    :return:
"""

def getRecommendations(prefs, person, score=0, similarity=sim_pearson):
    """
    给一个人进行物品推荐
    利用所有人对电影的打分，然后根据不同的人的相似度，预测目标用户对某个电影的打分，根据预测打分排序，就可以推送得分较高的电影
    :param prefs: 不同人对多部电影的评分字典
    :param person: 具体需要推荐业务的人的名字
    :param score: 推荐的预测得分阈值，大于这才推送，根据实际情况来给
    :param similarity: 相似度计算的方法，默认用的皮尔逊相似度(还可以写其它的方法)
    :return:format like -> [(物品推荐名称1, 及其可能的预测打分), ]
    """
    totals = {}
    simSums = {}
    # 不用和自己比较
    others = list(prefs.keys())
    others.remove(person)
    for other in others:
        sim = similarity(prefs, person, other)
        # 忽略相似度小于等于0的情况
        if sim <= 0:
            continue
        for item in prefs[other]:
            # 只对自己还没看过的电影进行评价
            if item not in prefs[person] or prefs[person][item] == 0:
                # 相似度 × 评价值；setdefault就是如果没有就新建，如果有，就取那个
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim  # 其人的打分乘以相似度(相似度越高的人就相当于权重越大，）
                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim
    # 其他人对电影的打分*其他人与这个人相似度，再求和，，最后除以相似度总和，得到这个人对这个没看的东西的预测打分
    rankings = [(item, total / simSums[item]) for item, total in totals.items() if total / simSums[item] >= score]
    # 对所有没看的东西的按打分高低排序一下，越前面的越可以推荐
    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings
# print(getRecommendations(critics,  "MichaelPhillips"))


def transformprefs(prefs):
    """
    将用户对电影的评分改为，电影对用户的适应度(将第一层字典的key从人名变成了电影名，第二层的key从电影名变成了人名)
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # 将把用户打分，赋值给电影的适应度
            result[item][person] = prefs[person][item]
    return result
# print(topMatches(transformprefs(critics), 'SupermanReturns'))  # 这就可以得到与SupermanReturns相似度较高的电影
# print(getRecommendations(transformprefs(critics), "JustMyLuck"))  # 这样得到的就是某个电影对用户的适应度


"""一般都是基于用户的协同过滤，但有一个缺点，就是当将用户与其他用户进行比较时，产生的计算时间也许会非常长。
而且如果在一个物品特别多的情况下，也许会很难找出相似用户。在数据集非常多的情况，基于物品的协同过滤表现更好。
就可以先找出物品的相似物品，这样做有2个好处：大量计算预先进行（计算物品相似度）、快速给用户推荐结果"""
def calculateSimilarItems(prefs, n=10):
    """
    物品之间，跟它相似度前n个的计算
    :param prefs: 不同人对多部电影的评分字典
    :param n: 前n个相似的
    :return: 一个字典，key为电影名称，值是一个其它电影跟它相关性排序的列表
    """
    result = {}
    # 把用户对物品的评分，改为物品对用户的适应度
    itemPrefs = transformprefs(prefs)
    c = 0
    for item in tqdm.tqdm(itemPrefs, desc="寻找相近课程"):
        c += 1
        # if c % 100 == 0:
        #     print("{} / {}".format(c, len(itemPrefs)))
        # 寻找相近的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result
# pprint.pprint(calculateSimilarItems(critics))


# 产生推荐列表
def getRecommendedItems(prefs, itemSim, user):
    """

    :param prefs: 不同人对多部电影的评分字典
    :param itemSim: 物品之间相似度的字典
    :param user: 具体需要推荐业务的人的名字
    :return: 针对user的推荐物品 --> [(名称, 预测打分),]
    """
    userRatings = prefs[user]  # user打分的电影
    scores = {}
    totalSim = {}
    for (item, rating) in userRatings.items():  # user这个人的所有打分的电影、对应分数
        # 循环遍历与当前物品相近的物品
        for (item2, similarity) in itemSim[item]:
            # 如果该用户已经对当前物品做过评价，则将其忽略
            if item2 in userRatings:
                continue
            # 打分和相似度的加权之和
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # user这个人对电影item打分了rating，找到这个电影相似度前几的电影，就开始循环，若user没打过分，
            # 就用相似度similarity * rating作为预测user可能对没看的电影item2的打分；
            # 当最外层循环进入到user的另外一部电影时，相似度前几的可能跟前面的就有重复的，就同样加权加起来，最后在除以所有的相似度的和

            # 某一电影的与其他电影的相似度之和
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    # 将经过加权的评分除以相似度，求出对这一电影的评分
    rankings = [(item, (score / totalSim[item])) for item, score in scores.items()]
    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings


def recommend(rating_dict, person):
    """基于用户的的协同过滤"""
    out = getRecommendations(rating_dict, person)
    print("基于用户的的协同过滤:")
    print(out)

    """基于物品的协同过滤"""
    similaritems = calculateSimilarItems(rating_dict, 8)  # 基于已有数据生成物品相似度，取前8个
    recommend_list = getRecommendedItems(rating_dict, similaritems, person)
    print("基于物品的协同过滤:")
    print(recommend_list)


if __name__ == '__main__':
    recommend(critics, "MichaelPhillips")
