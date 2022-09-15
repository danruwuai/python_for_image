#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import numpy as np
import os
import cv2 as cv
import read_packed_word as readpackedword

def get_packed_word_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if file.endswith("packed_word"))
  
    return file_list


def input_pack_word():
    print("________________________________________________________________")
    print("Design by Zhong")
    print("Creation time:2022/09/10")
    print("________________________________________________________________")
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_packed_word_list = get_packed_word_file(current_working_dir)
    # print(file_packed_word_list)
    # 循环查找packed_word的文件
    for file_packed_word in file_packed_word_list:
        print("获取的文件：", file_packed_word)
        # 获取packed_word对应的信息
        packed_info = file_packed_word[file_packed_word.find('__'):file_packed_word.find('.')+1]
        packed_height = packed_info[packed_info.find('x') + 1:packed_info.find('.') - 5]
        packed_width = packed_info[packed_info.find('__') + 2:packed_info.find('x')]
        packed_bayer = packed_info[packed_info.find('.') - 1:packed_info.find('.')]
        packed_bit = packed_info[packed_info.find('.') - 4:packed_info.find('.') - 2]
        # 字符串转int
        packed_height = int(packed_height)
        packed_width = int(packed_width)
        packed_bayer = int(packed_bayer)
        packed_bit = int(packed_bit)
        print("width:", packed_width)
        print("height:", packed_height)
        print("bayer:", packed_bayer)
        print("bit:", packed_bit)
        # 读取packed_word,raw_name
        frame_raw, raw_name, width = readpackedword.read_packed_word(file_packed_word, packed_height, packed_width,
                                                                     packed_bayer)
        frame_raw = frame_raw / 4095.0
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
        frame_raw = frame_raw.astype(np.uint8)
        cv.imwrite(raw_name+'.bmp', cv.cvtColor(frame_raw, cv.COLOR_RGBA2BGRA))
        print("################################################################")