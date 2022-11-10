import numpy as np


def do_awb(img):
    R = 768
    G = 512
    B = 1212
    img[:, :, 0] = img[:, :, 0] * R / 512
    img[:, :, 1] = img[:, :, 1] * G / 512
    img[:, :, 2] = img[:, :, 2] * B / 512
    img = img.astype(np.uint16)
    return img