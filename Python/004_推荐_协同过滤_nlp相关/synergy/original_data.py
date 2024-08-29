# coding=utf-8
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

users_info_path = r"./data/users.dat"
movies_info_path = r"./data/movies.dat"
ratings_info_path = r"./data/ratings.dat"

max_min_scale = lambda x: (x - min(x)) / (max(x) - min(x))


def dataReadUser(users_info_path):
    users_info = open(users_info_path).readlines()
    users_info = np.asarray([temp.replace("\n", "").split("::") for temp in users_info])
    users_data = dict(
        userId=users_info[:, 0].astype(np.int),
        gender=users_info[:, 1],
        ageGroup=users_info[:, 2].astype(np.int),
        occupation=users_info[:, 3].astype(np.int),
        postCode=users_info[:, 4]
    )
    users_data = pd.DataFrame(users_data)
    return users_data


def dataReadMovie(movies_info_path):
    movies_info = open(movies_info_path, encoding="ISO-8859-1").readlines()
    movies_info = np.asarray([temp.replace("\n", "").split("::") for temp in movies_info])
    movies_data = dict(
        movieId=movies_info[:, 0].astype(np.int),
        title_year=movies_info[:, 1],
        genres=movies_info[:, 2]
    )
    movies_data = pd.DataFrame(movies_data)
    return movies_data


def dataReadRating(ratings_info_path):
    ratings_info = open(ratings_info_path).readlines()
    ratings_info = np.asarray([temp.replace("\n", "").split("::") for temp in ratings_info])
    ratings_data = dict(
        userId=ratings_info[:, 0].astype(np.int),
        movieId=ratings_info[:, 1].astype(np.int),
        rating=ratings_info[:, 2].astype(np.int),
        timeStamp=ratings_info[:, 3].astype(np.int)
    )
    ratings_data = pd.DataFrame(ratings_data)
    return ratings_data


def users():
    """
    最后的users_data,index=usersId，columns是简单处理后的用户基础属性
    :return: 二维ndarray，各个用户之间根据基础属性得到的余弦相似度
    """
    users_data = dataReadUser(users_info_path)
    users_data = users_data.set_index("userId")  # 将userId设为索引
    users_data.loc[users_data["gender"] == "M", "gender"] = 0  # 将男性数值化为0
    users_data.loc[users_data["gender"] == "F", "gender"] = 1  # 将女性数值化为1
    users_data["ageGroup"] = users_data[["ageGroup"]].apply(max_min_scale)  # 将年龄组归一化
    users_data["occupation"] = users_data[["occupation"]].apply(max_min_scale)  # 职业也归一化
    users_data = users_data.drop(columns="postCode")  # 暂时丢弃postCode(邮编)
    # users_data.values   # 这个就是可以用用户的基础属性来计算用户之间的相似度
    # 用户之间的相似度
    users_similarity = cosine_similarity(users_data.values)
    return users_similarity


def movies():
    """
    movies_data,index=movieId, columns就是所有的电影有的类别
    :return: 二维ndarray，各部电影之间根据其分类得到的余弦相似度
    """
    movies_data = dataReadMovie(movies_info_path)
    movies_data = movies_data.set_index("movieId")  # 将movieId设为索引
    # 下面这不一定用得到，# 把电影名及年份拆开
    # movies_data["title"], movies_data["year"] = movies_data["title_year"].str.split("(", 1).str
    # movies_data = movies_data.drop(columns="title_year")

    # 获取电影的所有分类
    movies_data["genres"] = movies_data["genres"].str.split("|")
    genres_ = movies_data["genres"].values.tolist()
    genres = movies_data["gen"]
    genres = set(sum(genres_, []))

    # 新建一个电影属性表，默认为0，,将有这个属性的填充为1
    movies_attri = pd.DataFrame(np.zeros((movies_data.index.size, len(genres))), index=movies_data.index,
                                columns=genres)
    for movie_id in movies_data.index:
        for genre in movies_data.loc[movie_id, "genres"]:
            movies_attri.loc[movie_id, genre] = 1
    # 电影直接属性的相似度
    movies_similarity = cosine_similarity(movies_attri.values)
    return movies_similarity


def rating(if_dict=True):
    """
    得到用户与电影之间的rating
    :param if_dict: 默认True，结果就是一个字典 like --> {userID:{movieId2:rating2, movieId3:rating3, }, }
    :return:if_dict为False时，结果就是一个index=userid,columns=movieid,value=score的DataFrame
    """
    ratings_data = dataReadRating(ratings_info_path)
    if if_dict:
        result = {}  # 这比下面赋值得到DataFrame快了很多
        for key, values in ratings_data.groupby(by=["userId"]):
            result[key] = dict(zip(values["movieId"].values, values["rating"].values))
        return result
    else:
        ratings_matrix = pd.DataFrame({}, index=ratings_data["userId"].unique(),
                                      columns=ratings_data["movieId"].unique())

        # 循环赋值太慢了，跟下面是一样的
        # for i in range(ratings_data.shape[0]):
        #     temp = ratings_data.iloc[i]
        #     ratings_matrix.loc[temp["userId"], temp["movieId"]] = temp["rating"]

        # 按userId分组后，针对同一个用户的电影rating进行整体赋值
        for key, values in ratings_data.groupby(by=["userId"]):
            ratings_matrix.loc[key, values["movieId"].values] = values["rating"].values
        return ratings_matrix


if __name__ == '__main__':
    out = rating(if_dict=False)
    columns = sorted(list(out))
    out = out.reindex(columns=columns)
    out.to_csv("../z_finally/data/movie_rate.csv")
    # from synergy.filtering import recommend  # 就是直接用前面写好的推荐的框架来的
    # recommend(rating(), 15)  # 这个15是代表的userId
