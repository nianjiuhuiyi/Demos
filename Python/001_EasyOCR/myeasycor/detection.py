import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from PIL import Image
from collections import OrderedDict

import cv2
import numpy as np
from .craft_utils import getDetBoxes, adjustResultCoordinates
from .imgproc import resize_aspect_ratio, normalizeMeanVariance
from .craft import CRAFT

def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict

def test_net(canvas_size, mag_ratio, net, images, text_threshold, link_threshold, low_text, poly, device, estimate_num_chars=False):
    # resize
    imgs_resized, target_ratio, size_heatmap = resize_aspect_ratio(images, canvas_size,\
                                                                          interpolation=cv2.INTER_LINEAR, mag_ratio=mag_ratio)
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = normalizeMeanVariance(imgs_resized)     # [0, 1, 2, 3] to [0, 3, 1, 2]
    x = torch.from_numpy(x).permute(0, 3, 1, 2)    # [n, h, w, c] to [n, c, h, w]
    x = Variable(x)                # [c, h, w] to [b, c, h, w]
    x = x.to(device)

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_texts = y[:,:,:,0].cpu().data.numpy()
    score_links = y[:,:,:,1].cpu().data.numpy()

    # Post-processing      # 搞到这里了,得到的3个东西都是在原来的基础上加了一层列表
    boxes_list, polys_list, mappers_list = getDetBoxes(score_texts, score_links, text_threshold, link_threshold, low_text, poly, estimate_num_chars)

    # coordinate adjustment
    boxes_list = adjustResultCoordinates(boxes_list, ratio_w, ratio_h)
    polys_list = adjustResultCoordinates(polys_list, ratio_w, ratio_h)
    if estimate_num_chars:
        boxes_list = list(boxes_list)
        polys_list = list(polys_list)

    for i in range(len(polys_list)):
        for k in range(len(polys_list[i])):
            if estimate_num_chars:
                boxes_list[i][k] = (boxes_list[i][k], mappers_list[i][k])
            if polys_list[i][k] is None:
                polys_list[i][k] = boxes_list[i][k]

    return boxes_list, polys_list

def get_detector(trained_model, device='cpu'):
    net = CRAFT()

    if device == 'cpu':
        net.load_state_dict(copyStateDict(torch.load(trained_model, map_location=device)))
    else:
        net.load_state_dict(copyStateDict(torch.load(trained_model, map_location=device)))
        net = torch.nn.DataParallel(net).to(device)
        cudnn.benchmark = False

    net.eval()
    return net

def get_textbox(detector, images, canvas_size, mag_ratio, text_threshold, link_threshold, low_text, poly, device, optimal_num_chars=None):

    estimate_num_chars = optimal_num_chars is not None
    bboxes_list, polys_list = test_net(canvas_size, mag_ratio, detector, images, text_threshold, link_threshold, low_text, poly, device, estimate_num_chars)

    if estimate_num_chars:
        for i in range(len(polys_list)):
            polys_list[i] = [p for p, _ in sorted(polys_list[i], key=lambda x: abs(optimal_num_chars - x[1]))]

    results = []
    for k in range(len(polys_list)):
        result = []
        for i, box in enumerate(polys_list[k]):
            poly = np.array(box).astype(np.int32).reshape((-1))
            result.append(poly)
        results.append(result)
    return results
