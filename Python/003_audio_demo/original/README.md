主要是环境的准备，要使用python3.8：

- conda create -n audio python=3.8 -y
- conda activate audio
- git clone https://github.com/tyiannak/pyAudioAnalysis.git
- pip install -r ./requirements.txt
- pip install -e .

---

`./resources/datas`中：(resources里的内容在阿里云盘上。包括之前的数据和模型)

- standard文件夹中就是扭矩扳手拧到头后发出的声音;
- slip文件夹中是扭矩扳手正常扭动时的声音;
- music文件夹中是周杰伦的稻香;
- speak是说话的录音。

---

使用：

- train和test主要就是看classify_train.py，不同的模型就改对应的方法就好了。
- 回归regression_train.py缺乏csv标注文件。因为官方的回归demo中有2个csv文件，其中是对训练文件的一个打分(有点类似于情感打分)，我还没这个文件

