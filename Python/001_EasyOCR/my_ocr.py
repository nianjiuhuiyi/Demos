import os
import cv2
import torch
import tqdm
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import numpy as np
from myeasycor import easyocr
import warnings

warnings.filterwarnings("ignore")

system_judge = True if torch.cuda.is_available() else False
# 当配置文件决定使用GPU，且硬件支持的条件下才使用GPU
IF_GPU = True
device = all((IF_GPU, system_judge))

OCR_MODELS_PATH = "./resources/ocr_models"


class MyDataset(Dataset):
    def __init__(self, path):
        self.path = path
        self.files_name = os.listdir(path)
        self.files_name.sort(key=len)

    def __len__(self):
        return len(self.files_name)

    def __getitem__(self, index):
        image_path = os.path.join(self.path, self.files_name[index])
        img = Image.open(image_path)
        # RGB转BGR,不直接用opencv打开，opencv路径中不能存在中文

        if img.mode != "RGB":
            img = img.convert("RGB")

        image = np.array(img)
        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = torch.from_numpy(image.copy())
        return image, image_gray


def predict(image_path, save_path, batch_size=4):
    reader = easyocr.Reader(['ch_sim', 'en'], model_storage_directory=OCR_MODELS_PATH, gpu=device)
    datas = MyDataset(path=image_path)
    data_loader = DataLoader(dataset=datas, batch_size=batch_size)
    file_name = os.path.basename(image_path) + ".txt"  # 文件名跟pdf保持一致
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file = open(os.path.join(save_path, file_name), "w", encoding="utf-8")
    for images, images_gray in data_loader:
        images = images.numpy()
        images_gray = images_gray.numpy()
        outputs = reader.readtext(images, images_gray)
        torch.cuda.empty_cache()
        for output in outputs:
            output = np.asarray(output)
            text = output[:, 1].tolist()
            file.write("\n".join(text))
        file.flush()
    file.close()


if __name__ == '__main__':
    """
    注意：这里有个bug，一个文件下的图片，是一起处理的，但是这些图片的大小可能不同，
          那么在stack拼接时就会报错，所以后续用的时候，在上面数据处理时，
          先检查下每张图的大小，不同的要resize。
    """
    total_image_path = r"/home/songhui/temp_123/new_jpgs"
    txt_save_path = r"/home/songhui/temp_123/new_txt"
    img_dir_names = os.listdir(total_image_path)
    for img_dir_name in tqdm.tqdm(img_dir_names):
        img_dir = os.path.join(total_image_path, img_dir_name)
        try:
            predict(img_dir, txt_save_path, 4)
        except Exception as e:
            print("error: {}".format(img_dir_name))
    print("\nDone!")

