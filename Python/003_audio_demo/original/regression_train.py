from pyAudioAnalysis import audioTrainTest as aT

aT.feature_extraction_train_regression("./resources/datas/standard", 1, 1, aT.shortTermWindow, aT.shortTermStep, "svm", "svmSpeechEmotion", True)

"""
    缺乏标注的csv文件

"""