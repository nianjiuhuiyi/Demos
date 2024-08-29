import os

"""
    将声音进行切片,存成训练数据
"""

# audio_path = "demo.wav"
audio_path = "./resources/datas/people_speak.wav"

counts = 0
for i in range(0, 10, 2):
    command = f"ffmpeg -ss {i} -t 2 -i {audio_path} ./resources/datas/speak/{counts:02d}.wav"
    print(command)
    os.system(command)
    counts += 1
