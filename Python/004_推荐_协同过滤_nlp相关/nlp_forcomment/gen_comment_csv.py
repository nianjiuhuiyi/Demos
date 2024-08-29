import pandas as pd
import numpy as np

# np.random.seed(0)

path = "../feature/data/person_comment.csv"
old_data = pd.read_csv(path, index_col=0)
# exit()

new_data = pd.read_csv("./data/waimai_10k.csv", encoding="UTF-8")
new_data = new_data.values[:, 1]
choice = np.random.randint(0, new_data.shape[0], size=old_data.size)
new_data = new_data[choice].reshape(old_data.shape)
print(new_data)
print()
print()
out = pd.DataFrame(new_data, index=old_data.index, columns=old_data.columns)
print(out)
print(out.index)
print(out.columns)
# out.to_csv("comment.csv")

# data = pd.read_csv("comment.csv")
# print(data.columns)


# data = pd.read_csv("./data/waimai_10k.csv", encoding="UTF-8")
# print(data.sample(265)["review"].values)
# exit()
# positiva_data = data[data["label"] == 1]
# negative_data = data[data["label"] == 0]
# print(positiva_data.values)
# print(negative_data.values)