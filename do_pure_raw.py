#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from pickle import FALSE
import numpy as np
from matplotlib import pyplot as plt


def do_black_level_correction(image, bits):
    # 计算OB值，默认64(10 bit)
    image_obc = 16 * 2 ** (bits - 8)
    image[image < image_obc] = image_obc
    image = image - image_obc

    return image


def do_bayer_color(file_name, height, width, bayer):
    rgb_img = np.zeros(shape=(height, width, 3))
    R = rgb_img[:, :, 0]
    GR = rgb_img[:, :, 1]
    GB = rgb_img[:, :, 1]
    B = rgb_img[:, :, 2]
    # 0:B 1:GB 2:GR 3:R
    if bayer == 3 or bayer == "RGGB":
        R[::2, ::2] = file_name[::2, ::2]
        GR[::2, 1::2] = file_name[::2, 1::2]
        GB[1::2, ::2] = file_name[1::2, ::2]
        B[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer == 2 or bayer == "GRBG":
        GR[::2, ::2] = file_name[::2, ::2]
        R[::2, 1::2] = file_name[::2, 1::2]
        B[1::2, ::2] = file_name[1::2, ::2]
        GB[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer == 1 or bayer == "GBRG":
        GB[::2, ::2] = file_name[::2, ::2]
        B[::2, 1::2] = file_name[::2, 1::2]
        R[1::2, ::2] = file_name[1::2, ::2]
        GR[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer == 0 or bayer == "BGGR":
        B[::2, ::2] = file_name[::2, ::2]
        GB[::2, 1::2] = file_name[::2, 1::2]
        GR[1::2, ::2] = file_name[1::2, ::2]
        R[1::2, 1::2] = file_name[1::2, 1::2]
    else:
        print("no match bayer")
        return False
    return rgb_img


def bayer_cumuhistogram(image, pattern, max):
    R, GR, GB, B = bayer_channel_separation(image, pattern)
    R_hist = mono_cumuhistogram(R, max)
    GR_hist = mono_cumuhistogram(GR, max)
    GB_hist = mono_cumuhistogram(GB, max)
    B_hist = mono_cumuhistogram(B, max)
    return R_hist, GR_hist, GB_hist, B_hist


def mono_cumuhistogram(image, max):
    hist, bins = np.histogram(image, bins=range(0, max + 1))
    sum = 0
    for i in range(0, max):
        sum = sum + hist[i]
        hist[i] = sum
        return hist


def bayer_channel_separation(data, pattern):
    image_data = data
    # 0:B 1:GB 2:GR 3:R
    if pattern == 3 or pattern == "RGGB":
        R = image_data[::2, ::2]
        GR = image_data[::2, 1::2]
        GB = image_data[1::2, ::2]
        B = image_data[1::2, 1::2]
    elif pattern == 2 or pattern == "GRBG":
        GR = image_data[::2, ::2]
        R = image_data[::2, 1::2]
        B = image_data[1::2, ::2]
        GB = image_data[1::2, 1::2]
    elif pattern == 1 or pattern == "GBRG":
        GB = image_data[::2, ::2]
        B = image_data[::2, 1::2]
        R = image_data[1::2, ::2]
        GR = image_data[1::2, 1::2]
    elif pattern == 0 or pattern == "BGGR":
        B = image_data[::2, ::2]
        GB = image_data[::2, 1::2]
        GR = image_data[1::2, ::2]
        R = image_data[1::2, 1::2]
    else:
        print("no match pattern")
        print("pattern must be one of ： RGGB GRBG GBRG BGGR or 0 1 2 3")
        return FALSE
    return R, GR, GB, B


def histogram_show(frame_data, bits):
    out = frame_data
    max = 2 ** bits - 1
    hist, bins = np.histogram(out, bins=range(0, max))
    plt.figure(num='hist', figsize=(5, 6))
    plt.bar(range(len(hist)), hist)
    plt.show()
