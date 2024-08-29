# -*- coding: cp936 -*-
import numpy as np
import tqdm
import pprint

# һ���ֵ䣬��һ��key��������value������һ���ֵ䣬�ֵ�������key��Ӱ����value������
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
    ����ŷ����ü���������֮������ƶ�(���й�ͬ��Ӱ������������)
    :param prefs:��ͬ�˶Զಿ��Ӱ�������ֵ�
    :param person1:����һ������
    :param person2:����һ������
    :return: �����ŷʽ����ת��һ�£�����ԽС�����ƶ�Խ��ֵ��(0,1]֮��
    """
    # ���Ȱ���������û���ͬӵ�������ֵ�Ӱ���ҳ����������ǽ���һ���ֵ䣬�ֵ��key�ǵ�Ӱ���֣���Ӱ��ֵ����1
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    # ���û�й�֮ͬ��
    if len(si) == 0:
        return 0
    # ������������ͬ��Ӱ���ֵĵ�ƽ����
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in si])
    return 1 / (1 + np.sqrt(sum_of_squares))
# print(sim_distance(critics, "JackMatthews", "MickLaSalle"))


def sim_pearson(prefs, p1, p2):
    """
    ���������˵�Ƥ��ѷ���ϵ��,һ�����ڼ������������������ϵ�Ľ��̶ܳȣ�ȡֵ��[-1, 1]֮��
    :param prefs:ͬ�˶Զಿ��Ӱ�������ֵ�
    :return:
    """
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    # �������û�й�֮ͬ�����򷵻�0
    n = len(si)
    if n == 0:
        return 0
    # �Թ�ͬӵ�е���Ʒ�����֣��ֱ����
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    # ��ƽ����
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    # ��˻�֮��
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    # ����Ƥ��ѷ����ֵ
    num = pSum - (sum1 * sum2 / len(si))
    den = np.sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    return num / den
# print(sim_pearson(critics, "JackMatthews", "MickLaSalle"))


def tanimoto(a, b):
    """
    Tanimotoϵ��(�����������ϵĽ���/�������ϵĲ���),�൱��cosine����չ��Ҳ�����ڼ����ĵ����ݵ����ƶ�
    """
    c = [v for v in a if v in b]
    return float(len(c)) / (len(a) + len(b) - len(c))


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """
    ���һ��Ŀ���û������غ������ƶȸߵ���
    :param prefs: ��ͬ�˶Զಿ��Ӱ�������ֵ�
    :param person: ������Ҫ�Ƽ�ҵ����˵�����
    :param n:Ĭ��ǰ5��
    :param similarity: ���ƶȼ���ķ�����Ĭ���õ�Ƥ��ѷ���ƶ�
    :return:���س���Ϊn�ģ���person���ƶ���ߵ�n���˵��б�
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
    ��һ���˽�����Ʒ�Ƽ�
    ���������˶Ե�Ӱ�Ĵ�֣�Ȼ����ݲ�ͬ���˵����ƶȣ�Ԥ��Ŀ���û���ĳ����Ӱ�Ĵ�֣�����Ԥ�������򣬾Ϳ������͵÷ֽϸߵĵ�Ӱ
    :param prefs: ��ͬ�˶Զಿ��Ӱ�������ֵ�
    :param person: ������Ҫ�Ƽ�ҵ����˵�����
    :param score: �Ƽ���Ԥ��÷���ֵ������������ͣ�����ʵ���������
    :param similarity: ���ƶȼ���ķ�����Ĭ���õ�Ƥ��ѷ���ƶ�(������д�����ķ���)
    :return:format like -> [(��Ʒ�Ƽ�����1, ������ܵ�Ԥ����), ]
    """
    totals = {}
    simSums = {}
    # ���ú��Լ��Ƚ�
    others = list(prefs.keys())
    others.remove(person)
    for other in others:
        sim = similarity(prefs, person, other)
        # �������ƶ�С�ڵ���0�����
        if sim <= 0:
            continue
        for item in prefs[other]:
            # ֻ���Լ���û�����ĵ�Ӱ��������
            if item not in prefs[person] or prefs[person][item] == 0:
                # ���ƶ� �� ����ֵ��setdefault�������û�о��½�������У���ȡ�Ǹ�
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim  # ���˵Ĵ�ֳ������ƶ�(���ƶ�Խ�ߵ��˾��൱��Ȩ��Խ�󣬣�
                # ���ƶ�֮��
                simSums.setdefault(item, 0)
                simSums[item] += sim
    # �����˶Ե�Ӱ�Ĵ��*����������������ƶȣ�����ͣ������������ƶ��ܺͣ��õ�����˶����û���Ķ�����Ԥ����
    rankings = [(item, total / simSums[item]) for item, total in totals.items() if total / simSums[item] >= score]
    # ������û���Ķ����İ���ָߵ�����һ�£�Խǰ���Խ�����Ƽ�
    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings
# print(getRecommendations(critics,  "MichaelPhillips"))


def transformprefs(prefs):
    """
    ���û��Ե�Ӱ�����ָ�Ϊ����Ӱ���û�����Ӧ��(����һ���ֵ��key����������˵�Ӱ�����ڶ����key�ӵ�Ӱ�����������)
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # �����û���֣���ֵ����Ӱ����Ӧ��
            result[item][person] = prefs[person][item]
    return result
# print(topMatches(transformprefs(critics), 'SupermanReturns'))  # ��Ϳ��Եõ���SupermanReturns���ƶȽϸߵĵ�Ӱ
# print(getRecommendations(transformprefs(critics), "JustMyLuck"))  # �����õ��ľ���ĳ����Ӱ���û�����Ӧ��


"""һ�㶼�ǻ����û���Эͬ���ˣ�����һ��ȱ�㣬���ǵ����û��������û����бȽ�ʱ�������ļ���ʱ��Ҳ���ǳ�����
���������һ����Ʒ�ر�������£�Ҳ�������ҳ������û��������ݼ��ǳ���������������Ʒ��Эͬ���˱��ָ��á�
�Ϳ������ҳ���Ʒ��������Ʒ����������2���ô�����������Ԥ�Ƚ��У�������Ʒ���ƶȣ������ٸ��û��Ƽ����"""
def calculateSimilarItems(prefs, n=10):
    """
    ��Ʒ֮�䣬�������ƶ�ǰn���ļ���
    :param prefs: ��ͬ�˶Զಿ��Ӱ�������ֵ�
    :param n: ǰn�����Ƶ�
    :return: һ���ֵ䣬keyΪ��Ӱ���ƣ�ֵ��һ��������Ӱ���������������б�
    """
    result = {}
    # ���û�����Ʒ�����֣���Ϊ��Ʒ���û�����Ӧ��
    itemPrefs = transformprefs(prefs)
    c = 0
    for item in tqdm.tqdm(itemPrefs, desc="Ѱ������γ�"):
        c += 1
        # if c % 100 == 0:
        #     print("{} / {}".format(c, len(itemPrefs)))
        # Ѱ���������Ʒ
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result
# pprint.pprint(calculateSimilarItems(critics))


# �����Ƽ��б�
def getRecommendedItems(prefs, itemSim, user):
    """

    :param prefs: ��ͬ�˶Զಿ��Ӱ�������ֵ�
    :param itemSim: ��Ʒ֮�����ƶȵ��ֵ�
    :param user: ������Ҫ�Ƽ�ҵ����˵�����
    :return: ���user���Ƽ���Ʒ --> [(����, Ԥ����),]
    """
    userRatings = prefs[user]  # user��ֵĵ�Ӱ
    scores = {}
    totalSim = {}
    for (item, rating) in userRatings.items():  # user����˵����д�ֵĵ�Ӱ����Ӧ����
        # ѭ�������뵱ǰ��Ʒ�������Ʒ
        for (item2, similarity) in itemSim[item]:
            # ������û��Ѿ��Ե�ǰ��Ʒ�������ۣ��������
            if item2 in userRatings:
                continue
            # ��ֺ����ƶȵļ�Ȩ֮��
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # user����˶Ե�Ӱitem�����rating���ҵ������Ӱ���ƶ�ǰ���ĵ�Ӱ���Ϳ�ʼѭ������userû����֣�
            # �������ƶ�similarity * rating��ΪԤ��user���ܶ�û���ĵ�Ӱitem2�Ĵ�֣�
            # �������ѭ�����뵽user������һ����Ӱʱ�����ƶ�ǰ���Ŀ��ܸ�ǰ��ľ����ظ��ģ���ͬ����Ȩ������������ڳ������е����ƶȵĺ�

            # ĳһ��Ӱ����������Ӱ�����ƶ�֮��
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    # ��������Ȩ�����ֳ������ƶȣ��������һ��Ӱ������
    rankings = [(item, (score / totalSim[item])) for item, score in scores.items()]
    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings


def recommend(rating_dict, person):
    """�����û��ĵ�Эͬ����"""
    out = getRecommendations(rating_dict, person)
    print("�����û��ĵ�Эͬ����:")
    print(out)

    """������Ʒ��Эͬ����"""
    similaritems = calculateSimilarItems(rating_dict, 8)  # ������������������Ʒ���ƶȣ�ȡǰ8��
    recommend_list = getRecommendedItems(rating_dict, similaritems, person)
    print("������Ʒ��Эͬ����:")
    print(recommend_list)


if __name__ == '__main__':
    recommend(critics, "MichaelPhillips")
