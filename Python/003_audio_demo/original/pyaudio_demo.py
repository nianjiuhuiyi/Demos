from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import ShortTermFeatures
import matplotlib.pyplot as plt

[Fs, x] = audioBasicIO.read_audio_file("./resources/datas/standard/01.wav")
# 此音频是两个通道的，进行平均成一个通道; 不然reshape时会报错，详见：https://github.com/tyiannak/pyAudioAnalysis/issues/162
x = audioBasicIO.stereo_to_mono(x)

F, f_names = ShortTermFeatures.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
print(F.shape)

plt.subplot(2,1,1); plt.plot(F[0,:]); plt.xlabel('Frame no'); plt.ylabel(f_names[0])
plt.subplot(2,1,2); plt.plot(F[1,:]); plt.xlabel('Frame no'); plt.ylabel(f_names[1]); plt.show()


