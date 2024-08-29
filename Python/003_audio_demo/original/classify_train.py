from pyAudioAnalysis import audioTrainTest as aT

"""
    github上，wiki上写的demo的函数用的是 aT.feature_extraction_train，应该是没更新了，用下面这个aT.extract_features_and_train
"""


# 训练一个分类器
def train(method: str, for_music=False):
    """

    :param method: 使用哪种训练方法：可选的有  svm  knn   extratrees  gradientboosting  randomforest
    :param for_music: It is used only for the musical genre classifiers,类似于节拍，全都是节拍，设为True比较好
    :return:
    """
    # 此时数据列表的顺序决定着结果输出的顺序
    aT.extract_features_and_train(["./resources/datas/standard", "./resources/datas/speak", "./resources/datas/slip", "./resources/datas/music"],
                                  1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, method,
                                  f"./resources/models/{method}_4_classes", for_music)


def classify(audio_path, model_path, method):
    result = aT.file_classification(audio_path, model_path, method)
    return result


if __name__ == '__main__':
    """
        conda activate audio
    """
    # knn的训练结果不太行，gradientboosting似乎区分度更大
    method = "gradientboosting"   #  svm  knn   extratrees  gradientboosting  randomforest
    test_audio = "./resources/datas/test_english_speak.wav"       #  test_english_speak.wav  test_music_1.wav
    model_path = f"./resources/models/{method}_4_classes"

    # # 训练
    # train(method)

    result = classify(test_audio, model_path, method)
    print(result)
