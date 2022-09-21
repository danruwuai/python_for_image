#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from formatter import NullFormatter
from struct import pack
import numpy as np
import os
import sys
import cv2 as cv
import read_packed_word as readpackedword


# 获取packed_word文件列表
def get_packed_word_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):  # 遍历所有子目录        
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith('.packed_word') and '-yplane-' not in file and 'cplane' not in file))
        # print(file_list)
    return file_list


# 获取packed_word（s0）文件列表
def get_packed_word_s0_file(dir_path):
    file_list_s0 = []
    for root, dirs, files in os.walk(dir_path):  # 遍历所有子目录
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        # 获取文件名
        file_list_s0.extend(os.path.join("", file) for file in files if (file.endswith("packed_word") and "_s0." in file and "yplane" in file))
        # print(file_list_s0)
    return file_list_s0


# 获取lsc_raw文件列表
def get_lsc_raw_file(dir_path):
    file_list_lsc = []
    for root, dirs, files in os.walk(dir_path):  # 遍历所有子目录 
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        # 获取文件名
        file_list_lsc.extend(os.path.join("", file) for file in files if (file.endswith(".raw") and "_LSC_" in file and "_16_" in file))

    return file_list_lsc


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
        packed_info = file_packed_word[file_packed_word.find('__'):file_packed_word.find('.') + 1]
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
        frame_raw, raw_name, width, yuv_flag = readpackedword.read_packed_word(file_packed_word, packed_height, packed_width,
                                                                     packed_bayer, packed_bit)
        if raw_name == False:
            continue
        if yuv_flag == 1:
            frame_raw = frame_raw / 16
            frame_raw = frame_raw.astype(np.uint8)
            cv.imwrite(raw_name + '_yuv.bmp', cv.cvtColor(frame_raw, cv.COLOR_RGBA2BGRA))
        else:
            frame_raw = frame_raw / 16
            # cv.imwrite(f'{raw_name}bmp', frame_raw)
            # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
            frame_raw = frame_raw.astype(np.uint8)
            cv.imwrite(raw_name + '.bmp', cv.cvtColor(frame_raw, cv.COLOR_RGBA2BGRA))
        print("################################################################")


def input_lsc_raw():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    # 处理LCS文件
    file_lsc_raw_list = get_lsc_raw_file(current_working_dir)
    for file_lsc_raw in file_lsc_raw_list:
        print("获取的文件：", file_lsc_raw)
        # 获取packed_word对应的信息
        packed_info = file_lsc_raw[file_lsc_raw.find('__'):file_lsc_raw.find('.') + 1]
        packed_height = packed_info[packed_info.find('x') + 1:packed_info.find('_16_')]
        packed_width = packed_info[packed_info.find('__') + 2:packed_info.find('x')]
        packed_bayer = packed_info[packed_info.find('_16_') + 4:packed_info.find('_LSC_') - 1]
        packed_bit = 16
        # 字符串转int
        packed_height = int(packed_height)
        packed_width = int(packed_width)
        packed_bayer = int(packed_bayer)
        packed_bit = packed_bit
        print("width:", packed_width)
        print("height:", packed_height)
        print("bayer:", packed_bayer)
        print("bit:", packed_bit)
        # 读取raw,raw_name
        frame_raw, raw_name = readpackedword.read_lsc_raw(file_lsc_raw, packed_height, packed_width,
                                                                     packed_bayer)
        frame_raw = frame_raw / 16
        # 由于16bit转12bit，会有超出255的值。
        frame_raw = np.clip(frame_raw, 0, 255)
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。

        frame_raw = frame_raw.astype(np.uint8)
        cv.imwrite(raw_name + '.bmp', cv.cvtColor(frame_raw, cv.COLOR_RGBA2BGRA))
        print("################################################################")


# 处理packed_word_s0的图片
def input_pack_word_s0():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_packed_word_s0_list = get_packed_word_s0_file(current_working_dir)
    # print(file_packed_word_s0_list)
    # 循环查找packed_word_s0的文件
    for file_packed_word_s0 in file_packed_word_s0_list:
        print("获取的文件：", file_packed_word_s0)
        # 获取packed_word对应的信息
        packed_info = file_packed_word_s0[file_packed_word_s0.find('__'):file_packed_word_s0.find('.') + 1]
        packed_height = packed_info[packed_info.find('x') + 1:packed_info.find('.') - 6]
        packed_width = packed_info[packed_info.find('__') + 2:packed_info.find('x')]
        packed_bit = packed_info[packed_info.find('.') - 5:packed_info.find('.') - 3]
        packed_pw_width = file_packed_word_s0[file_packed_word_s0.find('PW')+2:file_packed_word_s0.find('-PH')]
        packed_ph_height = file_packed_word_s0[file_packed_word_s0.find('PH')+2:file_packed_word_s0.find('-BW')]
        packed_BW_width = file_packed_word_s0[file_packed_word_s0.find('BW')+2:file_packed_word_s0.find('__')]
        # 如果没有对应的ph,pw,bw,赋值-1
        if packed_ph_height == file_packed_word_s0[1:-1] or packed_BW_width == file_packed_word_s0[1:-1] or packed_pw_width == file_packed_word_s0[1:-1]:
            packed_BW_width=packed_ph_height=packed_pw_width = '-1'
        # 字符串转int
        packed_height = int(packed_height)
        packed_width = int(packed_width)
        packed_bit = int(packed_bit)
        packed_pw_width = int(packed_pw_width)
        packed_ph_height= int(packed_ph_height)
        packed_BW_width = int(packed_BW_width)
        print("width:", packed_width)
        print("height:", packed_height)
        print("bit:", packed_bit)
        print("line_width:", packed_pw_width)
        print("frame_height:", packed_ph_height)
        print("Bayer_W:", packed_BW_width)
        # 读取cplane名字
        yplane_name = file_packed_word_s0
        # 读取yplane名字
        cplane_name = yplane_name.replace('yplane', 'cplane')
        # 读取packed_word_s0_yplan,raw_name
        frame_yplane, frame_yplane_name, width = readpackedword.read_packed_word_yplane(yplane_name, packed_height, packed_width, packed_bit, packed_ph_height, packed_pw_width, packed_BW_width)
        if frame_yplane_name == False:
            continue
        """
        # 输出对应的bmp图片
        frame_yplane = frame_yplane / 16
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片,所以需要RGB转换未BGR再输出。
        frame_yplane = frame_yplane.astype(np.uint8)
        cv.imwrite(yplane_name + '.bmp', frame_yplane)
        """
        # 如果存在cplane的packed_word,进行yuv转换
        if os.path.exists(cplane_name):
            # 读取packed_word_s0_cplan,raw_name
            frame_cb, frame_cr, frame_cplane_name, width = readpackedword.read_packed_word_cplane(cplane_name, packed_height // 2, packed_width, packed_bit, packed_ph_height // 2, packed_pw_width, packed_BW_width)
            if frame_cplane_name == False:
                continue
            """
            frame_cb = frame_cb / 16
            frame_cr = frame_cr / 16
            # cv.imwrite(f'{raw_name}bmp', frame_raw)
            # imwrite默认输出的是BGR图片,所以需要RGB转换未BGR再输出。
            frame_cb = frame_cb.astype(np.uint8)
            frame_cr = frame_cr.astype(np.uint8)
            cv.imwrite(frame_cplane_name + '_cb.bmp', frame_cb)
            cv.imwrite(frame_cplane_name + '_cr.bmp', frame_cr)
            """
            # 处理ycbcr数据
            frame_ycbcr = readpackedword.do_ycbcr(frame_yplane, frame_cb, frame_cr, packed_height, width, frame_yplane_name)
            frame_ycbcr = frame_ycbcr.astype(np.uint8)
            yuv_name = frame_yplane_name.replace('_12_', '_8_')
            cv.imwrite(yuv_name + '_yuv.bmp', cv.cvtColor(frame_ycbcr, cv.COLOR_RGBA2BGRA))
        else:  # 如果不存在cplane的packed_word,直接显示灰度图
            frame_yplane = frame_yplane / 16
            # cv.imwrite(f'{raw_name}bmp', frame_raw)
            # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
            frame_yplane = frame_yplane.astype(np.uint8)
            cv.imwrite(frame_yplane_name + '.bmp', frame_yplane)
        print("################################################################")
        
        
if __name__ == '__main__':
    # 添加输入信息
    if len(sys.argv) > 1:
        author = sys.argv[1]
        if author == "Zhong":
            print("________________________________________________________________")
            print("Design by Zhongguojun")
            print("Creation time:2022/09/10")
            print("________________________________________________________________")
    input_pack_word()
    input_lsc_raw()
    input_pack_word_s0()
