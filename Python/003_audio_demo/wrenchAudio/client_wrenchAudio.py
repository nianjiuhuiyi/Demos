"""
    程序运行后，可按回车退出程序！

    sample: python client_wrenchAudio.py [DEVICE_INDEX]
"""

import json
import wave  # python标准库
import traceback
import time
import requests
import threading
import queue

import pyaudio
from pyAudioAnalysis import audioTrainTest
# from scipy.io import wavfile

import numpy as np
from wavfile import get_type_count  # 参看 from scipy.io import wavfile

import sys
import os
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

import configure as cfg
from configure import NJBS_AUDIO_CONTENT

g_Exit = False
que = queue.Queue(maxsize=2)

CHUNK = 1024  # 定义数据流块,,或者给1024？
FORMAT = pyaudio.paInt16  # 量化位数（音量级划分）
CHANNELS = 2  # 声道数;声道数：可以是单声道或者是双声道
RATE = 44100  # 采样率;采样率：一秒内对声音信号的采集次数，常用的有8kHz, 16kHz, 32kHz, 48kHz, 11.025kHz, 22.05kHz, 44.1kHz(44100)
RECORD_SECONDS = 1  #
WAVE_OUTPUT_FILENAME = f"./{time.time()}.wav"  # 获取音频格式的临时wav文件路径

method = "randomforest"  # svm  knn   extratrees  gradientboosting  randomforest
model_path = f"./weights/{method}_4_classes"


def post(url, headers, request_data):
    try:
        res = requests.post(url, headers=headers, data=request_data)
        print(res.status_code, res.text)
    except Exception:
        print("消息发送失败，一分钟后再次尝试...")
        time.sleep(60)


def get_format(pid, aid, rate, channel):
    """
    得到音频数据直接转numpy数组所需要的格式
    :param pid: pyaudio.PyAudio() 的实例化对象
    :param aid: audio 音频设备打开后的stream流
    :param rate: 采样率
    :param channel: 声道数
    :return: tuple(dtype, count),: ('<i2', 88064)
    """

    wf = wave.Wave_write(WAVE_OUTPUT_FILENAME)  # 默认二进制写入
    wf.setnchannels(channel)  # 配置声道数
    wf.setsampwidth(pid.get_sample_size(FORMAT))  # 配置量化位数
    wf.setframerate(rate)

    # 总共2秒时长
    for _ in range(0, int(rate / CHUNK * RECORD_SECONDS * 2)):
        # exception_on_overflow 默认是True，树莓派需要这为False，不然一会儿就报 “OSError: [Errno -9981] Input overflowed”
        _data = aid.read(CHUNK, exception_on_overflow=False)  # 读取chunk个字节 保存到data中
        wf.writeframes(_data)
    wf.close()

    out = get_type_count(WAVE_OUTPUT_FILENAME)
    # 获取格式后，删除那个临时音频文件
    os.remove(WAVE_OUTPUT_FILENAME)
    return out


def exit_program():
    # 回车退出程序
    global g_Exit

    while True:
        if g_Exit:
            break

        s = input()
        if s == "":
            g_Exit = True
            break


def audio_record(DEVICE_INDEX):
    global g_Exit, CHANNELS, RATE

    p = pyaudio.PyAudio()
    try:
        deviceInfo = p.get_device_info_by_index(DEVICE_INDEX)
        deviceName = deviceInfo["name"]
        assert "USB Audio Device" in deviceName, "Error: wrong mic device index!"
    except Exception as e:
        traceback.print_exc()
        g_Exit = True
    else:
        CHANNELS = deviceInfo["maxInputChannels"] if deviceInfo.get("maxInputChannels") is not None else CHANNELS
        RATE = deviceInfo["defaultSampleRate"] if deviceInfo.get("defaultSampleRate") is not None else RATE
        RATE = int(RATE)

        # 打开设备
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        frames_per_buffer=CHUNK,
                        input=True,
                        input_device_index=DEVICE_INDEX)

        dtype, count = get_format(p, stream, RATE, CHANNELS)
        print((dtype, count), "\n")

        wavFrames = list()  # 存放单此音频检测的数据

        while True:
            frame = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                # exception_on_overflow 默认是True，树莓派需要这为False，不然一会儿就报 “OSError: [Errno -9981] Input overflowed”
                data = stream.read(CHUNK, exception_on_overflow=False)  # 读取chunk个字节 保存到data中
                # wf.writeframes(data)
                frame.append(data)

            wavFrames.append(b''.join(frame))

            # 第一次进入时长只有1秒，跳过；后续都是2秒时长数据再进入模型分类
            if len(wavFrames) != 2:
                continue

            # 直接将读取的音频文件转换为numpy数组，避免磁盘两次IO读写
            single = np.frombuffer(b''.join(wavFrames), dtype=dtype, count=count)

            # 时刻保持更新，同样保证在post发送消息阻塞时程序依旧能正常运行
            if que.full():
                que.get_nowait()
            que.put_nowait(single)

            # 去掉前一秒的数据
            wavFrames.pop(0)

            if g_Exit:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()


def run(dev_id):
    global g_Exit

    # 用于音频采集的线程
    t_record = threading.Thread(target=audio_record, args=(dev_id,), daemon=True)
    t_record.start()
    # 拿些时间，子线程先去做初始化，有问题后续就直接退出了
    time.sleep(1)

    # 用于退出的线程
    t_exit = threading.Thread(target=exit_program, daemon=True)
    t_exit.start()
    time.sleep(1)

    while True:
        if g_Exit:
            time.sleep(1)
            break
        try:
            single = que.get()
            # my_file_classification是去库里源码添加的，直接将读取的音频转为numpy数组的single
            a = time.time()
            result = audioTrainTest.my_file_classification(RATE, single, model_path, method)
            b = time.time()
            print("detect time: {:.2f}ms".format(b * 1000 - a * 1000))
        except Exception:
            # result = audioTrainTest.file_classification(WAVE_OUTPUT_FILENAME, model_path, method)
            print("需要去修改audioTrainTest中的源码，才能直接传入numpy数组！")
            g_Exit = True
            time.sleep(1)
            break
        else:
            print(result)
            # 四个类别，环境音(0.0)、套筒扳手拆(1.0)、扭矩扳手装(2.0)、扭矩扳手拧到位(3.0)；要看训练模型时给的类别顺序
            if result[0] == 3.0:
                NJBS_AUDIO_CONTENT['flag'] = 1
            else:
                NJBS_AUDIO_CONTENT['flag'] = 0

            NJBS_AUDIO_CONTENT["timeStamp"] = int(round(time.time() * 1000))
            cfg.REQUEST_JSON["content"] = json.dumps(NJBS_AUDIO_CONTENT)
            request_data = json.dumps(cfg.REQUEST_JSON)
            print(request_data)

            post(url=cfg.URL, headers=cfg.HEADERS, request_data=request_data)
            print("\n")
    print("成功退出！")


if __name__ == '__main__':
    print(__doc__)
    device_id = 1  # usb设备的index,一般插入的usb麦克风索引依次是 1、2、3、4，且名字里是带 “USB Audio Device”

    args = sys.argv
    if (len(args) == 2) and (args[1].isdigit()):
        device_id = int(args[1])

    run(dev_id=device_id)
