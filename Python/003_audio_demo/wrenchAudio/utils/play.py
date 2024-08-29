import wave
import pyaudio
from tqdm import tqdm
import numpy as np
from pyAudioAnalysis import audioTrainTest

import wave

if __name__ == '__main__':
    CHUNK = 1024
    RECORD_SECONDS = 1
    method = "gradientboosting"   # svm  knn   extratrees  gradientboosting  randomforest

    wf = wave.open(r"C:\Users\Administrator\Desktop\ademo\01.wav", "rb")  # 到位
    # wf = wave.open(r"C:\Users\Administrator\Desktop\ademo\slip.wav", "rb")    # 拧螺丝的声音
    # wf = wave.open(r"C:\Users\Administrator\Desktop\ademo\speak.wav", "rb")    # speak

    RATE = wf.getframerate()

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    wavFrames = list()  # 存放单此音频检测的数据
    while True:
        frame = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = wf.readframes(CHUNK)
            frame.append(data)

        wavFrames.append(b''.join(frame))
        if len(wavFrames) != 2:
            continue

        try:
            single = np.frombuffer(b''.join(wavFrames), dtype='<i2', count=88064)
        except Exception as e:
            print(e)
            break

        result = audioTrainTest.my_file_classification(RATE, single,
                                                       f"E:\\SDGproject\\wrenchAudio\\weights\\{method}_4_classes",
                                                       method)
        print(result)

        wavFrames.pop(0)  # 去掉前一秒的数据

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()
