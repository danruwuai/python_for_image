#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# from pickle import FALSE
import numpy as np
from matplotlib import pyplot as plt


def do_black_level_correction(image, bits):
    # 计算OB值，默认64(10 bit)
    image_obc = 16 * 2 ** (bits - 8)
    image[image < image_obc] = image_obc
    image = image - image_obc

    return image


def do_bayer_color(file_name, height, width, bayer):
    rgb_img = np.zeros(shape=(height, width, 4))
    R = rgb_img[:, :, 0]
    GR = rgb_img[:, :, 1]
    GB = rgb_img[:, :, 1]
    B = rgb_img[:, :, 2]
    # 0:B 1:GB 2:GR 3:R
    if bayer in [3, "RGGB"]:
        R[::2, ::2] = file_name[::2, ::2]
        GR[::2, 1::2] = file_name[::2, 1::2]
        GB[1::2, ::2] = file_name[1::2, ::2]
        B[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer in [2, "GRBG"]:
        GR[::2, ::2] = file_name[::2, ::2]
        R[::2, 1::2] = file_name[::2, 1::2]
        B[1::2, ::2] = file_name[1::2, ::2]
        GB[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer in [1, "GBRG"]:
        GB[::2, ::2] = file_name[::2, ::2]
        B[::2, 1::2] = file_name[::2, 1::2]
        R[1::2, ::2] = file_name[1::2, ::2]
        GR[1::2, 1::2] = file_name[1::2, 1::2]
    elif bayer in [0, "BGGR"]:
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


def mono_cumuhistogram(image, max):  # sourcery skip: avoid-builtin-shadow
    hist, bins = np.histogram(image, bins=range(max + 1))
    sum = 0
    for i in range(max):
        sum = sum + hist[i]
        hist[i] = sum
        return hist


def bayer_channel_separation(data, pattern):
    image_data = data
    # 0:B 1:GB 2:GR 3:R
    if pattern in [3, "RGGB"]:
        R = image_data[::2, ::2]
        GR = image_data[::2, 1::2]
        GB = image_data[1::2, ::2]
        B = image_data[1::2, 1::2]
    elif pattern in [2, "GRBG"]:
        GR = image_data[::2, ::2]
        R = image_data[::2, 1::2]
        B = image_data[1::2, ::2]
        GB = image_data[1::2, 1::2]
    elif pattern in [1, "GBRG"]:
        GB = image_data[::2, ::2]
        B = image_data[::2, 1::2]
        R = image_data[1::2, ::2]
        GR = image_data[1::2, 1::2]
    elif pattern in [0, "BGGR"]:
        B = image_data[::2, ::2]
        GB = image_data[::2, 1::2]
        GR = image_data[1::2, ::2]
        R = image_data[1::2, 1::2]
    else:
        print("no match pattern")
        print("pattern must be one of ： RGGB GRBG GBRG BGGR or 0 1 2 3")
        return False
    return R, GR, GB, B


def bayer_channel_integrration(R, GR, GB, B, pattern):
    # ----------------------------------------------------------------
    #   Objective: combin data into a raw according to pattern
    #   Input：
    #       R, GR, GB, B：   the four separate channels (Quarter resolution)
    #       pattern:    RGGB, GBRG, GBRG, BGGR or 0 1 2 3
    #   Output:
    #       data (Full resolution image)
    # ----------------------------------------------------------------
    size = np.shape(R)
    data = np.empty((size[0] * 2, size[1] * 2), dtype=np.float32)
    if pattern in [3, "RGGB"]:
        data[::2, ::2] = R
        data[::2, 1::2] = GR
        data[1::2, ::2] = GB
        data[1::2, 1::2] = B
    elif pattern in [2, "GRBG"]:
        data[::2, ::2] = GR
        data[::2, 1::2] = R
        data[1::2, ::2] = B
        data[1::2, 1::2] = GB
    elif pattern in [1, "GBRG"]:
        data[::2, ::2] = GB
        data[::2, 1::2] = B
        data[1::2, ::2] = R
        data[1::2, 1::2] = GR
    elif pattern in [0, "BGGR"]:
        data[::2, ::2] = B
        data[::2, 1::2] = GB
        data[1::2, ::2] = GR
        data[1::2, 1::2] = R
    else:
        print("no match pattern")
        print("pattern must be one of ： RGGB GRBG GBRG BGGR or 0 1 2 3")
        return False
    return data


def histogram_show(frame_data, bits):
    out = frame_data
    max = 2 ** bits - 1
    hist, bins = np.histogram(out, bins=range(0, max))
    plt.figure(num='hist', figsize=(5, 6))
    plt.bar(range(len(hist)), hist)
    plt.show()


def raw_to_csv(image, raw_height, raw_width, bayer, name):
    height = raw_height // 2
    width = raw_width // 2
    # 创建CSV表格数据，内容赋值空
    csv_data = np.full([4 * (height + 3), width], -1)
    csv_data = csv_data.astype('str')
    # 0:B 1:GB 2:GR 3:R
    if bayer in [3, "RGGB"]:
        R_data = image[::2, ::2]
        GR_data = image[::2, 1::2]
        GB_data = image[1::2, ::2]
        B_data = image[1::2, 1::2]
    elif bayer in [2, "GRBG"]:
        GR_data = image[::2, ::2]
        R_data = image[::2, 1::2]
        B_data = image[1::2, ::2]
        GB_data = image[1::2, 1::2]
    elif bayer in [1, "GBRG"]:
        GB_data = image[::2, ::2]
        B_data = image[::2, 1::2]
        R_data = image[1::2, ::2]
        GR_data = image[1::2, 1::2]
    elif bayer in [0, "BGGR"]:
        B_data = image[::2, ::2]
        GB_data = image[::2, 1::2]
        GR_data = image[1::2, ::2]
        R_data = image[1::2, 1::2]
    else:
        print("no match bayer")
        return False
    csv_data[0, 0] = 'R'
    R_data = R_data.astype('str')
    csv_data[1: height + 3 - 2, 0: width] = R_data
    csv_data[height + 3, 0] = 'GR'
    GR_data = GR_data.astype('str')
    csv_data[height + 3 + 1: 2 * (height + 3) - 2, 0: width] = GR_data
    csv_data[2 * (height + 3), 0] = 'GB'
    GB_data = GB_data.astype('str')
    csv_data[2 * (height + 3) + 1: 3 * (height + 3) - 2, 0: width] = GB_data
    csv_data[3 * (height + 3), 0] = 'B'
    B_data = B_data.astype('str')
    csv_data[3 * (height + 3) + 1: 4 * (height + 3) - 2, 0: width] = B_data
    # 替换csv_data数据里的-1为空
    csv_data[csv_data == '-1'] = ''
    np.savetxt(f'{name}.csv', csv_data, delimiter=",", fmt='%s')
    print("输出raw统计数据:", f'{name}.csv')
