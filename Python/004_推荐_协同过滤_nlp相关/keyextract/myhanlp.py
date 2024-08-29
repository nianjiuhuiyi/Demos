
import os
import glob
from pyhanlp import HanLP
'''pyhanlp的简单使用参考：https://cloud.tencent.com/developer/article/1424476'''
# root_path = r"C:\Users\dell\Desktop\results"
root_path = r"../finally_results"
dirs_name = os.listdir(root_path)
for dir_name in dirs_name:
    files_path = os.path.join(root_path, dir_name)
    files = glob.glob(files_path + "/*.txt")
    for file in files:
        with open(file, encoding="utf-8") as f:
            txt = f.read()
        # 关键词提取
        doc_kewwords = HanLP.extractKeyword(txt, 10)

        # 文本摘要
        doc_sentence = HanLP.extractSummary(txt, 10)  # 结果不是很理想
        print(os.path.basename(file), doc_kewwords)
    print("--"*100)

"""这个效果感觉比较一般"""

