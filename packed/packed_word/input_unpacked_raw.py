#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import os
import cv2 as cv
import do_pure_raw
import read_unpack_raw as read_unpackraw
# from matplotlib import pyplot as plt


# import raw_image_show as show


def get_raw_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("raw") and os.path.isfile(file)))

    return file_list


def load_raw():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_raw_list = get_raw_file(current_working_dir)
    # print(file_raw_list)
    # 循环查找raw的文件
    for file_raw in file_raw_list:
        print("获取的文件：", file_raw)
        # 获取raw对应的信息
        raw_info = file_raw[file_raw.find('__'):file_raw.find('.') + 1]
        raw_height = raw_info[raw_info.find('x') + 1:raw_info.find('.') - 5]
        raw_width = raw_info[raw_info.find('__') + 2:raw_info.find('x')]
        raw_bayer = raw_info[raw_info.find('.') - 1:raw_info.find('.')]
        raw_bit = raw_info[raw_info.find('.') - 4:raw_info.find('.') - 2]
        # 字符串转int
        raw_height = int(raw_height)
        raw_width = int(raw_width)
        raw_bayer = int(raw_bayer)
        raw_bit = int(raw_bit)
        print("width:", raw_width)
        print("height:", raw_height)
        print("bayer:", raw_bayer)
        print("bit:", raw_bit)
        frame_data = read_unpackraw.read_unpack_file(file_raw, raw_height, raw_width, raw_bit)
        # image = frame_data / 4095.
        # show.raw_image_show_thumbnail(image, raw_height, raw_width)
        #do_pure_raw.histogram_show(frame_data, raw_bit)
        rgb_data = do_pure_raw.do_bayer_color(frame_data, raw_height, raw_width, raw_bayer)
        # rgb_data = do_pure_raw.do_black_level_correction(rgb_data, raw_bit)
        # raw_image_show_fakecolor(rgb_data, raw_height, raw_width, raw_bit)
        frame_rgb = rgb_data / (2 ** (raw_bit - 8))
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
        frame_rgb = frame_rgb.astype(np.uint8)
        raw_name = file_raw[:file_raw.find('.')]
        cv.imwrite(raw_name + '.bmp', cv.cvtColor(frame_rgb, cv.COLOR_RGBA2BGRA))
        print("################################################################")


"""
def raw_image_show_fakecolor(image, height, width, bits):
    x = width / 100
    y = height / 100
    image = image / (2.0 ** bits - 1)
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(image, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')


if __name__ == "__main__":
    print("################################################################")
    print("Design by Zhong")
    print("Creation time:2022/09/10")
    print("################################################################")

    load_raw()
"""