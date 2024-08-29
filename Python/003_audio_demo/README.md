- [original](./original/README.md)：这是对[pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis)这个项目最初的尝试。
- [wrenchAudio](./wrenchAudio/README.md)：是扭矩扳手在pyAudioAnalysis的基础上改了，封装了一下自己的东西。

---

---

- 音频录取，用ffmpeg，代码实现：[教程](https://blog.csdn.net/qq_41004932/article/details/117090385)。 
- 声音特征提取，分类，一个很完整的[教程](http://www.taodudu.cc/news/show-5257195.html?action=onClick)。 
- linux：
  - 可以用命令 “aplay -l”（这时所有输出，包括视频）或者 “arecord -l”(这就是只看音频设备) 
  - lsusb 看哪些usb连接了



下面是关于**pyaudio**的一些基本使用：

### 1.1 获取设备信息

```python
import pyaudio
p = pyaudio.PyAudio()  
for i in range(p.get_device_count()):
	print(p.get_device_info_by_index(i), "\n")
```

### 1.2 录音demo

​	在音频处理中，**chunk**（也称为帧）是指音频信号中的一小段连续采样数据。每个chunk通常包含几毫秒到几百毫秒的音频数据，具体取决于采样率和帧率。在数字音频中，chunk是数字信号的基本单位，它们被用于压缩、存储、传输和处理音频数据。在音频处理中，通常需要对每个chunk进行分析、处理或转换，以实现各种音频效果和功能。

```python
import wave        # python标准库
import traceback
import threading
import time
import sys
import pyaudio

CHUNK = 1024  # 定义数据流块,还可是其它值
FORMAT = pyaudio.paInt16  # 量化位数（音量级划分）
CHANNELS = 1  # 声道数;声道数：可以是单声道(1)或者是双声道(2),还要看硬件支持不
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
		# RECORD_SECONDS 来控制单次录音时长
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream_obj.read(CHUNK)   # 读取chunk个字节 保存到data中
            wf_obj.writeframes(data)

        counts += 1
        print(counts)


def run(audio_name):
    global CHANNELS, RATE, g_Exit
    p = pyaudio.PyAudio()    # 实例化

    try:
        deviceInfo = p.get_device_info_by_index(DEVICE_INDEX)
    except Exception as e:
        traceback.print_exc()
    else:
        deviceName = deviceInfo["name"]
        assert "USB Audio Device" in deviceName, "Error: wrong mic device index!"
		# 通过读取硬件信息去修正配置
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
```

写入wav文件，还有别的方式，但大差不差

```python
# 写入文件
# wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")  # 打开wav文件创建一个音频对象wf，开始写WAV文件
wf = wave.Wave_write(WAVE_OUTPUT_FILENAME)  # 一个意思，默认就是wb，这样才有提示

wf.setnchannels(CHANNELS)  # 配置声道数
wf.setsampwidth(p.get_sample_size(FORMAT))  # 配置量化位数
wf.setframerate(RATE)  # 配置采样率

# frames = []  # 定义一个列表   # （123）可以先定义一个列表全部存起来，然后一起写入，也可以一次次写入
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  # 循环，采样率11025 / 256 * 5
    print(i)
    data = stream.read(CHUNK)  # 读取chunk个字节 保存到data中
    # frames.append(data)  # 向列表frames中添加数据data   # （123）
    wf.writeframes(data)
    print(data)
    break

stream.stop_stream()
stream.close()  # 关闭
p.terminate()  # 终结

# wf.writeframes(b''.join(frames))             # 转换为二进制数据写入文件  # （123）
wf.close()
```

### 1.3. 录音数据直接转ndarray

参考[地址](https://blog.51cto.com/u_16175447/6728618)。里面有：有 np.frombuffer,以及pyaudio获取默认设备。

​	除了上面，我自己也有根据“pyAudioAnalysis”库进行探索，它里面读取wav文件用的是第三方库：“from scipy.io import wavfile”。然后这个库会直接把.wav音频文件读成ndarray。

​	所以在做扭矩扳手音频识别时，一开始使用python的标准库“wave”调用麦克风，存成本地.wav音频文件，再调用“pyAudioAnalysis”库进行本地音频文件读写分类，涉及到了两次磁盘IO，然后我就用了np.frombuffer直接把数据从读取时的二进制buffer转成ndarray（但是时间上的花费主要还是在模型分类，而不是.wav文件的磁盘写入和读取）

​	只写部分代码，其它差不多：

```python
wavFrames = list()  # 存放单此音频检测的数据
while True:
    frame = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        # exception_on_overflow 默认是True，树莓派需要这为False，不然一会儿就报 “OSError: [Errno -9981] Input overflowed”
        data = stream.read(CHUNK, exception_on_overflow=False)  # 读取chunk个字节 保存到data中
        frame.append(data)

    wavFrames.append(b''.join(frame))

    # 第一次进入时长只有1秒，跳过；后续都是2秒时长数据再进入模型分类
    if len(wavFrames) != 2:
        continue

    # 直接将读取的音频文件转换为numpy数组，避免磁盘两次IO读写
    single = np.frombuffer(b''.join(wavFrames), dtype=dtype, count=count)
```

注：

- 上面16行代码得到的“single”就是ndarray，就是“pyAudioAnalysis”库做音频分类要的ndarray。
- 16行传入的参数：“dtype”、“count”是计算得来的，是从“pyAudioAnalysis”库读取音频文件中去一步步debug，看它读取音频文件时这俩参数是啥得来的。（所以时间长了你一定记不住这怎么来的了，但不重要，不要去多想，等后续再用得到的时候，再去分析debug一次，也是很快的）
  - 但对于这次来说，单声道，两秒，dtype='<i2', count=88064  作为参考。

### 1.4 播放demo

当需要在执行其他程序时同时播放音频，可以使用回调的方式播放,[地址参考](https://cloud.tencent.com/developer/article/1451526?from=15425)，示例代码如下：

```python
import pyaudio
import wave
from tqdm import tqdm

def play_audio(wave_path):
    CHUNK = 1024

    wf = wave.open(wave_path, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    datas = []
    while len(data) > 0:
        data = wf.readframes(CHUNK)
        datas.append(data)

    for d in tqdm(datas):
        stream.write(d)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()

play_audio("output.wav")
```

#### 回调的方式

​	还有另一个回调[教程](https://zhuanlan.zhihu.com/p/71235612)参考。

```python
import pyaudio
import wave
from tqdm import tqdm
import time

def play_audio_callback(wave_path):
    CHUNK = 1024

    wf = wave.open(wave_path, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    # read data
    stream.start_stream()

    while stream.is_active():
        time.sleep(0.1)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()

play_audio_callback("output.wav")
```

