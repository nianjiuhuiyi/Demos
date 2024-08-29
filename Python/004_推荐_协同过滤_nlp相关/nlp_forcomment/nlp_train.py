import os
import pandas as pd
from snownlp import seg, sentiment, SnowNLP

# 自带的文件，训练
# seg.train(r"E:\Anaconda3\Lib\site-packages\snownlp\seg\data.txt")
# seg.save("seg.marshal")

# 得到我的训练样本
# data = pd.read_csv("./data/waimai_10k.csv", encoding="UTF-8")
# positiva_data = data[data["label"] == 1]
# negative_data = data[data["label"] == 0]
#
# positive_out = open("./data/positive.txt", "w", encoding="utf-8")
#
# for a_review in positiva_data["review"]:
#     positive_out.write("{}\n".format(a_review))
#     positive_out.flush()
# positive_out.close()
#
# negative_out = open("./data/negative.txt", "w", encoding="utf-8")
# for a_review in negative_data["review"]:
#     negative_out.write("{}\n".format(a_review))
#     negative_out.flush()
# negative_out.close()


# 开始训练
# sentiment.train("./data/negative.txt", "./data/positive.txt")
# sentiment.save("sentiment2.marshal")


# 测试
q = SnowNLP(r"asdfgh")
print(q.sentiments)