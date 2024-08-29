import pyaudio
import wave
import traceback
import threading
import time
import sys

CHUNK = 1024  # 定义数据流块,,或者给1024？
FORMAT = pyaudio.paInt16  # 量化位数（音量级划分）
CHANNELS = 1  # 声道数;声道数：可以是单声道或者是双声道
RATE = 44100  # 采样率;采样率：一秒内对声音信号的采集次数，常用的有8kHz, 16kHz, 32kHz, 48kHz, 11.025kHz, 22.05kHz, 44.1kHz(44100)
RECORD_SECONDS = 1  # 录音秒数
DEVICE_INDEX = 1  # usb设备的index,一般插入的usb麦克风索引依次是 1、2、3、4，且名字里是带 “USB Audio Device”

g_Exit = False


def record(stream_obj, wf_obj):
    global g_Exit

    counts = 0
    while True:
        if g_Exit:
            break

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream_obj.read(CHUNK)
            wf_obj.writeframes(data)

        counts += 1
        print(counts)


def run(audio_name):
    global CHANNELS, RATE, g_Exit
    p = pyaudio.PyAudio()

    try:
        deviceInfo = p.get_device_info_by_index(DEVICE_INDEX)
    except Exception as e:
        traceback.print_exc()
    else:
        deviceName = deviceInfo["name"]
        assert "USB Audio Device" in deviceName, "Error: wrong mic device index!"

        CHANNELS = deviceInfo["maxInputChannels"] if deviceInfo.get("maxInputChannels") is not None else CHANNELS
        RATE = deviceInfo["defaultSampleRate"] if deviceInfo.get("defaultSampleRate") is not None else RATE
        RATE = int(RATE)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=DEVICE_INDEX)

    # 写入文件
    wf = wave.Wave_write(audio_name)  # 一个意思，默认就是wb，这样才有提示
    wf.setnchannels(CHANNELS)  # 配置声道数
    wf.setsampwidth(p.get_sample_size(FORMAT))  # 配置量化位数
    wf.setframerate(RATE)  # 配置采样率

    t1 = threading.Thread(target=record, args=(stream, wf))
    t1.start()

    print("Press enter to exit!")
    while True:
        str = input()
        if str == "":
            g_Exit = True
            break
    time.sleep(1.5)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf.close()
    print("Done!")


if __name__ == '__main__':
    args = sys.argv
    file_name = ""
    if len(args) == 1:
        file_name = "temp.wav"
    elif len(args) == 2:
        file_name = args[1]
    else:
        print("Error，demo like: 'python sampling *.wav'")
        exit(0)
    run(file_name)
