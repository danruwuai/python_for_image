#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import time
import math
import os
import cv2
import numpy as np
import raw_image_show
import do_pure_raw
from multiprocessing import Process, Queue, Lock


def get_lsc_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("lsc") and os.path.isfile(file)))

    return file_list


def get_lsc_mask_file(dir_path, sdblk_mask):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        for file in files:
            if (file.endswith("lsc") and os.path.isfile(file)) and file[:17] == sdblk_mask:
                return file, True

    return False, False


def get_sdblk_file(dir_path, sdblk_mask):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        for file in files:
            if (file.endswith("sdblk") and os.path.isfile(file)) and file[:17] == sdblk_mask:
                return file, True

    return False, False


def import_exif_hwtbl(hwtbl_file_path):
    width = 4096
    height = 3072

    if width == 0 or height == 0:
        return False
    blk_wd = math.floor(width / (2 * 16))
    blk_ht = math.floor(height / (2 * 16))
    blk_wd_last = (width - blk_wd * 2 * 15) / 2
    blk_ht_last = (height - blk_ht * 2 * 15) / 2
    sdblk_file_path = os.path.splitext(hwtbl_file_path)[0] + ".sdblk"

    with open(hwtbl_file_path, "r") as hwtbl_file:
        with open(sdblk_file_path, "w") as sdblk_file:
            sdblk_file.write('%9d%9d%9d%9d%9d%9d%9d%9d\n' % (0, 0, blk_wd, blk_ht, 15, 15, blk_wd_last, blk_ht_last))
            for line in hwtbl_file:
                if "blockNum" not in line:
                    data = line.split(", ")[:6]
                    for i in data:
                        sdblk_file.write("%9d%9d" % (int(i, 16) & 0xFFFF, int(i, 16) >> 16))
                    sdblk_file.write("\n")


def import_exif_sdblk(sdblk_file_path):
    hwtbl_file_path = os.path.splitext(sdblk_file_path)[0] + ".hwtbl"
    data_num = 9
    with open(sdblk_file_path, "r") as sdblk_file:
        with open(hwtbl_file_path, "w") as hwtbl_file:
            lsc_info = sdblk_file.readline()
            blk_offset_x = int(lsc_info[0 * data_num: 1 * data_num])
            blk_offset_y = int(lsc_info[1 * data_num: 2 * data_num])
            blk_wd = int(lsc_info[2 * data_num: 3 * data_num])
            blk_ht = int(lsc_info[3 * data_num: 4 * data_num])
            blk_num_x = int(lsc_info[4 * data_num: 5 * data_num])
            blk_num_y = int(lsc_info[5 * data_num: 6 * data_num])
            blk_wd_last = int(lsc_info[6 * data_num: 7 * data_num])
            blk_ht_last = int(lsc_info[7 * data_num: 8 * data_num])
            width = blk_wd * blk_num_x * 2 + blk_wd_last * 2 + blk_offset_x * 2
            height = blk_ht * 2 * blk_num_y + blk_ht_last * 2 + blk_offset_y * 2
            print(blk_offset_x, blk_offset_y, blk_wd, blk_ht, blk_num_x, blk_num_y, blk_wd_last, blk_ht_last)
            print(lsc_info, width, height)
            # next(sdblk_file)
            for line in sdblk_file:
                if "blockNum" not in line:
                    data_all = line.split("\n")
                    data = data_all[0]
                    for i in range(6):
                        hwtbl_file.write("0x%08x, " % (int(data[i * 2 * data_num: (i * 2 + 1) * data_num]) + (
                                int(data[(i * 2 + 1) * data_num: (i * 2 + 2) * data_num]) << 16)))
                    hwtbl_file.write("\n")


def get_lsc_file_list():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_lsc_list = get_lsc_file(current_working_dir)
    # print(file_raw_list)
    # 循环查找raw的文件
    for lsc_file_path in file_lsc_list:
        print("获取的文件：", lsc_file_path)
        transform_lsc_data(lsc_file_path)


def transform_lsc_data(lsc_file_path):
    hwtbl_file_path = os.path.splitext(lsc_file_path)[0] + ".hwtbl"
    sdblk_file_path = os.path.splitext(lsc_file_path)[0] + ".sdblk"
    print(hwtbl_file_path, sdblk_file_path)
    with open(hwtbl_file_path, "w") as hwtbl_file:
        with open(sdblk_file_path, "w") as sdblk_file:
            lsc_new = 0
            lsc_size = os.path.getsize(lsc_file_path)
            print(lsc_size)
            lsc_file = np.fromfile(lsc_file_path, count=lsc_size, dtype="uint16")
            width = lsc_file[0] + np.left_shift(lsc_file[1], 8)
            height = lsc_file[2] + np.left_shift(lsc_file[3], 8)
            blk_num_w = lsc_file[4] + np.left_shift(lsc_file[5], 8)
            blk_num_h = lsc_file[6] + np.left_shift(lsc_file[7], 8)
            blk_num_x = lsc_file[8] + np.left_shift(lsc_file[9], 8)
            blk_num_y = lsc_file[10] + np.left_shift(lsc_file[11], 8)
            blk_wd = lsc_file[12] + np.left_shift(lsc_file[13], 8)
            blk_ht = lsc_file[14] + np.left_shift(lsc_file[15], 8)
            blk_wd_last = lsc_file[16] + np.left_shift(lsc_file[17], 8)
            blk_ht_last = lsc_file[18] + np.left_shift(lsc_file[19], 8)
            unknown = lsc_file[20] + np.left_shift(lsc_file[21], 8)
            if abs(unknown - blk_wd_last) <= 1:
                blk_wd_last1 = unknown
                blk_ht_last1 = lsc_file[22] + np.left_shift(lsc_file[23], 8)
                unknown = lsc_file[24] + np.left_shift(lsc_file[25], 8)
                lsc_new = 1
            if lsc_new == 1:
                print(width, height, blk_num_w, blk_num_h, blk_num_x, blk_num_y, blk_wd, blk_ht,
                      blk_wd_last, blk_ht_last, blk_wd_last1, blk_ht_last1, unknown)
                sdblk_file.write('%9d%10d%10d%10d%10d%10d%10d%10d%10d%10d\n' % (
                    0, 0, blk_wd, blk_ht, blk_num_x, blk_num_y, blk_wd_last, blk_ht_last, blk_wd_last1, blk_ht_last1))
                sdblk_data_path = lsc_file[26:]
                sdblk_data = np.zeros(len(sdblk_data_path)*2)
                sdblk_data[::2] = np.bitwise_and(sdblk_data_path, 0xFF)
                sdblk_data[1::2] = np.right_shift(np.bitwise_and(sdblk_data_path, 0xFF00), 8)
                sdblk_data = sdblk_data.astype("uint32")
                for i in range((blk_num_w - 1) * (blk_num_h - 1) * 4 * 12):
                    if i % 3 == 0:
                        sdblk_file.write('%9d' % (sdblk_data_path[i // 3 * 4] + np.left_shift(np.bitwise_and(sdblk_data_path[i // 3 * 4 + 1],0xf),16)))
                    elif i % 3 == 1:
                        sdblk_file.write('%9d' % (np.right_shift(np.bitwise_and(sdblk_data_path[i // 3 * 4 + 1], 0xfff0), 4) + np.left_shift(np.bitwise_and(sdblk_data_path[i // 3 * 4 + 2],0xff),12)))
                    else:
                        sdblk_file.write('%9d' % (np.right_shift(np.bitwise_and(sdblk_data_path[i // 3 * 4 + 2], 0xff00), 8) + np.left_shift(np.bitwise_and(sdblk_data_path[i // 3 * 4 + 3],0xfff),8)))
                    if i % 2 == 1:
                        hwtbl_file.write("0x%08x, " % (sdblk_data_path[i-1] + (int(sdblk_data_path[i]) << 16)))
                    if i % 16 == 15:
                        hwtbl_file.write("\n")
                    if i % 12 == 11:
                        sdblk_file.write('\n')
            else: 
                print(width, height, blk_num_w, blk_num_h, blk_num_x, blk_num_y, blk_wd, blk_ht,
                      blk_wd_last, blk_ht_last, unknown)
                sdblk_file.write('%9d%9d%9d%9d%9d%9d%9d%9d\n' % (
                    0, 0, blk_wd, blk_ht, blk_num_x, blk_num_y, blk_wd_last, blk_ht_last))
                for i in range((blk_num_w - 1) * (blk_num_h - 1) * 4 * 12):
                    sdblk_file.write('%9d' % (lsc_file[i + 22]))
                    if i % 2 == 1:
                        hwtbl_file.write("0x%08x, " % (lsc_file[i + 21] + (int(lsc_file[i + 22]) << 16)))
                    if i % 12 == 11:
                        sdblk_file.write('\n')
                        hwtbl_file.write("\n")


def transf_lsc(sdblk_file_path, bayer):  # sourcery skip: low-code-quality
    sdblk_name = os.path.splitext(sdblk_file_path)[0]
    data_num = 9
    with open(sdblk_file_path, "r") as sdblk_file:
        dict_sdblk = {}
        lsc_info = sdblk_file.readline()
        dict_sdblk["blk_offset_x"] = int(lsc_info[0 * data_num: 1 * data_num])
        if len(lsc_info) < 10 * data_num:
            sdblk_new = 0
            if lsc_info[2 * data_num:2 * data_num + 1] != " ":
                dict_sdblk["blk_offset_y"] = int(lsc_info[1 * (data_num + 1): 2 * (data_num + 1)])
                dict_sdblk["blk_wd"] = int(lsc_info[2 * (data_num + 1): 3 * (data_num + 1)])
                dict_sdblk["blk_ht"] = int(lsc_info[3 * (data_num + 1): 4 * (data_num + 1)])
                blk_num_x = int(lsc_info[4 * (data_num + 1): 5 * (data_num + 1)])
                blk_num_y = int(lsc_info[5 * (data_num + 1): 6 * (data_num + 1)])
                dict_sdblk["blk_wd_last"] = int(lsc_info[6 * (data_num + 1): 7 * (data_num + 1)])
                dict_sdblk["blk_ht_last"] = int(lsc_info[7 * (data_num + 1): 8 * (data_num + 1)])
            else:
                dict_sdblk["blk_offset_y"] = int(lsc_info[1 * data_num: 2 * data_num])
                dict_sdblk["blk_wd"] = int(lsc_info[2 * data_num: 3 * data_num])
                dict_sdblk["blk_ht"] = int(lsc_info[3 * data_num: 4 * data_num])
                blk_num_x = int(lsc_info[4 * data_num: 5 * data_num])
                blk_num_y = int(lsc_info[5 * data_num: 6 * data_num])
                dict_sdblk["blk_wd_last"] = int(lsc_info[6 * data_num: 7 * data_num])
                dict_sdblk["blk_ht_last"] = int(lsc_info[7 * data_num: 8 * data_num])
            dict_sdblk["width"] = dict_sdblk["blk_wd"] * blk_num_x * 2 + dict_sdblk[
                "blk_wd_last"] * 2 + dict_sdblk["blk_offset_x"] * 2
            dict_sdblk["height"] = dict_sdblk["blk_ht"] * 2 * blk_num_y + dict_sdblk[
                "blk_ht_last"] * 2 + dict_sdblk["blk_offset_y"] * 2
            print(dict_sdblk["blk_offset_x"], dict_sdblk["blk_offset_y"], dict_sdblk["blk_wd"], dict_sdblk["blk_ht"],
                  blk_num_x, blk_num_y, dict_sdblk["blk_wd_last"], dict_sdblk["blk_ht_last"])
            print(lsc_info, dict_sdblk["width"], dict_sdblk["height"])
            dict_sdblk["blk_y"] = blk_num_y + 1
            dict_sdblk["blk_x"] = blk_num_x + 1
            sdblk_data_0 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_1 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_2 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_3 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            flag = 0
            # next(sdblk_file)
            for line in sdblk_file:
                if "blockNum" not in line:
                    data_all = line.split("\n")
                    data = data_all[0]
                    for i in range(12):
                        if flag % 4 == 0:
                            if i == 11:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            else:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk["blk_x"], i] = \
                                    (32768 - int(data[i * data_num: (i + 1) * data_num])) / 4096
                        elif flag % 4 == 1:
                            if i == 11:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            else:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 - int(data[i * data_num: (i + 1) * data_num])) / 4096
                        elif flag % 4 == 2:
                            if i == 11:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            else:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 - int(data[i * data_num: (i + 1) * data_num])) / 4096
                        else:
                            if i == 11:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                            else:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 - int(data[i * data_num: (i + 1) * data_num])) / 4096
                    flag = flag + 1
        else:
            sdblk_new = 1
            if lsc_info[2 * data_num:2 * data_num + 1] != " ":
                dict_sdblk["blk_offset_y"] = int(lsc_info[1 * (data_num + 1): 2 * (data_num + 1)])
                dict_sdblk["blk_wd"] = int(lsc_info[2 * (data_num + 1): 3 * (data_num + 1)])
                dict_sdblk["blk_ht"] = int(lsc_info[3 * (data_num + 1): 4 * (data_num + 1)])
                blk_num_x = int(lsc_info[4 * (data_num + 1): 5 * (data_num + 1)])
                blk_num_y = int(lsc_info[5 * (data_num + 1): 6 * (data_num + 1)])
                dict_sdblk["blk_wd_last0"] = int(lsc_info[6 * (data_num + 1): 7 * (data_num + 1)])
                dict_sdblk["blk_ht_last0"] = int(lsc_info[7 * (data_num + 1): 8 * (data_num + 1)])
                dict_sdblk["blk_wd_last1"] = int(lsc_info[8 * (data_num + 1): 9 * (data_num + 1)])
                dict_sdblk["blk_ht_last1"] = int(lsc_info[9 * (data_num + 1): 10 * (data_num + 1)])
            else:
                dict_sdblk["blk_offset_y"] = int(lsc_info[1 * data_num: 2 * data_num])
                dict_sdblk["blk_wd"] = int(lsc_info[2 * data_num: 3 * data_num])
                dict_sdblk["blk_ht"] = int(lsc_info[3 * data_num: 4 * data_num])
                blk_num_x = int(lsc_info[4 * data_num: 5 * data_num])
                blk_num_y = int(lsc_info[5 * data_num: 6 * data_num])
                dict_sdblk["blk_wd_last0"] = int(lsc_info[6 * data_num: 7 * data_num])
                dict_sdblk["blk_ht_last0"] = int(lsc_info[7 * data_num: 8 * data_num])
                dict_sdblk["blk_wd_last1"] = int(lsc_info[8 * data_num: 9 * data_num])
                dict_sdblk["blk_ht_last1"] = int(lsc_info[9 * data_num: 10 * data_num])
            dict_sdblk["width"] = dict_sdblk["blk_wd"] * (blk_num_x - 2) * 2 + dict_sdblk[
                "blk_wd_last0"] * 2 + dict_sdblk["blk_wd_last1"] * 2 + dict_sdblk["blk_offset_x"] * 2
            dict_sdblk["height"] = dict_sdblk["blk_ht"] * 2 * (blk_num_y - 2) + dict_sdblk[
                "blk_ht_last0"] * 2 + dict_sdblk["blk_ht_last1"] * 2 + dict_sdblk["blk_offset_y"] * 2
            print(dict_sdblk["blk_offset_x"], dict_sdblk["blk_offset_y"], dict_sdblk["blk_wd"], dict_sdblk[
                "blk_ht"], blk_num_x, blk_num_y, dict_sdblk["blk_wd_last0"], dict_sdblk["blk_ht_last0"], dict_sdblk[
                      "blk_wd_last1"], dict_sdblk["blk_ht_last1"])
            print(lsc_info, dict_sdblk["width"], dict_sdblk["height"])
            dict_sdblk["blk_y"] = blk_num_y
            dict_sdblk["blk_x"] = blk_num_x
            sdblk_data_0 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_1 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_2 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            sdblk_data_3 = np.zeros(shape=(dict_sdblk["blk_y"], dict_sdblk["blk_x"], 12))
            flag = 0
            # next(sdblk_file)
            for line in sdblk_file:
                if "blockNum" not in line:
                    data_all = line.split("\n")
                    data = data_all[0]
                    for i in range(12):
                        if flag % 4 == 0:
                            if i == 11:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 8
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768 * 16:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 16
                            else:
                                sdblk_data_0[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 * 16 - int(data[i * data_num: (i + 1) * data_num]))/4096/16
                        elif flag % 4 == 1:
                            if i == 11:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 8
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768 * 16:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 16
                            else:
                                sdblk_data_1[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 * 16 - int(data[i * data_num: (i + 1) * data_num]))/4096/16
                        elif flag % 4 == 2:
                            if i == 11:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 8
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768 * 16:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 16
                            else:
                                sdblk_data_2[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 * 16 - int(data[i * data_num: (i + 1) * data_num]))/4096/16
                        else:
                            if i == 11:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 8
                            elif int(data[i * data_num: (i + 1) * data_num]) < 32768 * 16:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = int(data[i * data_num: (i + 1) * data_num]) / 4096 / 16
                            else:
                                sdblk_data_3[flag // (4 * dict_sdblk["blk_x"]), flag // 4 % dict_sdblk[
                                    "blk_x"], i] = (32768 * 16 - int(data[i * data_num: (i + 1) * data_num]))/4096/16
                    flag = flag + 1
        start = time.time()
        """
        lsc_data_0 = cal_lsc_data(sdblk_data_0, dict_sdblk)
        lsc_data_1 = cal_lsc_data(sdblk_data_1, dict_sdblk)
        lsc_data_2 = cal_lsc_data(sdblk_data_2, dict_sdblk)
        lsc_data_3 = cal_lsc_data(sdblk_data_3, dict_sdblk)
        """
        q = Queue()
        lock = Lock()
        dict = {}
        obj0 = Process(target=cal_lsc_data, args=(sdblk_data_0, dict_sdblk, "lsc0", sdblk_new, q, lock))
        obj1 = Process(target=cal_lsc_data, args=(sdblk_data_1, dict_sdblk, "lsc1", sdblk_new, q, lock))
        obj2 = Process(target=cal_lsc_data, args=(sdblk_data_2, dict_sdblk, "lsc2", sdblk_new, q, lock))
        obj3 = Process(target=cal_lsc_data, args=(sdblk_data_3, dict_sdblk, "lsc3", sdblk_new, q, lock))
        obj0.start()
        obj1.start()
        obj2.start()
        obj3.start()
        dict.update(q.get())
        dict.update(q.get())
        dict.update(q.get())
        dict.update(q.get())
        lsc_data_0 = dict["lsc0"]
        lsc_data_1 = dict["lsc1"]
        lsc_data_2 = dict["lsc2"]
        lsc_data_3 = dict["lsc3"]
        end = time.time()
        print(end - start)
        # 图像显示lsc
        # 　raw_image_show.raw_image_show_3D(lsc_data_0, blk_y * 3, blk_x * 4)
        obj = Process(target=raw_image_show.raw_image_show_lsc, args=(
            lsc_data_0, lsc_data_1, lsc_data_2, lsc_data_3, dict_sdblk["height"] / 2, dict_sdblk["width"] / 2,
            sdblk_name))  # args以元组的形式给子进程func函数传位置参数
        # kwargs以字典的形式给子进程func函数传关键字参数
        # kwargs={'name': '小杨', 'age': 18}
        obj.start()  # 执行子进程对象
        # 输出csv
        lsc_to_csv(lsc_data_0, sdblk_name)
        if bayer in [3, "RGGB"]:
            return lsc_data_0, lsc_data_1, lsc_data_2, lsc_data_3
        elif bayer in [2, "GRBG"]:
            return lsc_data_1, lsc_data_0, lsc_data_3, lsc_data_2
        elif bayer in [1, "GBRG"]:
            return lsc_data_2, lsc_data_3, lsc_data_0, lsc_data_1
        elif bayer in [0, "BGGR"]:
            return lsc_data_3, lsc_data_2, lsc_data_1, lsc_data_0
        else:
            print("no match bayer")
            return False


"""
def cal_lsc_data(sdblk_data, dict_sdblk):
    lsc_data = np.zeros(shape=(dict_sdblk["height"] // 2, dict_sdblk["width"] // 2))
    for j in range(dict_sdblk["blk_y"]):
        for i in range(dict_sdblk["blk_x"]):
            if i < dict_sdblk["blk_x"] - 1 and j < dict_sdblk["blk_y"] - 1:
                lsc_data[j * dict_sdblk["blk_ht"]:(j+1) * dict_sdblk["blk_ht"],
                i * dict_sdblk["blk_wd"]:(i+1) * dict_sdblk["blk_wd"]] =\
                    func_sdblk(sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd"])
            else:
                lsc_data[j * dict_sdblk["blk_ht"]:j * dict_sdblk["blk_ht"] + dict_sdblk[
                "blk_ht_last"], i *dict_sdblk["blk_wd"]:i * dict_sdblk["blk_wd"]+dict_sdblk[
                "blk_wd_last"]] = func_sdblk(sdblk_data[j, i,:], dict_sdblk["blk_ht_last"], dict_sdblk["blk_wd_last"])
    return lsc_data
"""


def cal_lsc_data(sdblk_data, dict_sdblk, name, sdblk_new, q, lock):
    lsc_data = np.zeros(shape=(dict_sdblk["height"] // 2, dict_sdblk["width"] // 2))
    if sdblk_new == 0:
        for j in range(dict_sdblk["blk_y"]):
            for i in range(dict_sdblk["blk_x"]):
                if i < dict_sdblk["blk_x"] - 1 and j < dict_sdblk["blk_y"] - 1:
                    lsc_data[j * dict_sdblk["blk_ht"]:(j + 1) * dict_sdblk["blk_ht"], i * dict_sdblk[
                        "blk_wd"]:(i + 1) * dict_sdblk["blk_wd"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd"])
                elif i < dict_sdblk["blk_x"] - 1 and j == dict_sdblk["blk_y"] - 1:
                    lsc_data[j * dict_sdblk["blk_ht"]:j * dict_sdblk["blk_ht"] + dict_sdblk[
                        "blk_ht_last"], i * dict_sdblk["blk_wd"]:(i + 1) * dict_sdblk["blk_wd"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last"], dict_sdblk["blk_wd"])
                elif i == dict_sdblk["blk_x"] - 1 and j < dict_sdblk["blk_y"] - 1:
                    lsc_data[j * dict_sdblk["blk_ht"]:(j + 1) * dict_sdblk["blk_ht"], i * dict_sdblk[
                        "blk_wd"]:i * dict_sdblk["blk_wd"] + dict_sdblk["blk_wd_last"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd_last"])
                else:
                    lsc_data[j * dict_sdblk["blk_ht"]:j * dict_sdblk["blk_ht"] + dict_sdblk[
                        "blk_ht_last"], i * dict_sdblk["blk_wd"]:i * dict_sdblk["blk_wd"] + dict_sdblk[
                        "blk_wd_last"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last"], dict_sdblk["blk_wd_last"])
    else:
        for j in range(dict_sdblk["blk_y"]):
            for i in range(dict_sdblk["blk_x"]):
                if i == 0 and j == 0:
                    lsc_data[0:dict_sdblk["blk_ht_last0"], 0:dict_sdblk["blk_wd_last0"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last0"],
                        dict_sdblk["blk_wd_last0"])
                elif j == 0 and i < dict_sdblk["blk_x"] - 1:
                    lsc_data[0:dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"]:dict_sdblk["blk_wd_last0"] + i * dict_sdblk[
                        "blk_wd"]] = func_sdblk(sdblk_data[j, i, :], dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd"])
                elif i == 0 and j < dict_sdblk["blk_y"] - 1:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:j * dict_sdblk[
                        "blk_ht"] + dict_sdblk["blk_ht_last0"], 0:dict_sdblk["blk_wd_last0"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd_last0"])
                elif j == 0 and i == dict_sdblk["blk_x"] - 1:
                    lsc_data[0:dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd_last0"] + (i - 1) * dict_sdblk[
                        "blk_wd"]: dict_sdblk["blk_wd_last0"] + (i - 1) * dict_sdblk["blk_wd"] + dict_sdblk[
                        "blk_wd_last1"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd_last1"])
                elif i == 0 and j == dict_sdblk["blk_y"] - 1:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:dict_sdblk["blk_ht_last0"] + (
                            j - 1) * dict_sdblk["blk_ht"] + dict_sdblk["blk_ht_last1"], 0:dict_sdblk[
                        "blk_wd_last0"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last1"], dict_sdblk["blk_wd_last0"])
                elif i == dict_sdblk["blk_x"] - 1 and j == dict_sdblk["blk_y"] - 1:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:dict_sdblk["blk_ht_last0"] + (
                            j - 1) * dict_sdblk["blk_ht"] + dict_sdblk["blk_ht_last1"], dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"]:dict_sdblk["blk_wd_last0"] + (i - 1) * dict_sdblk[
                        "blk_wd"] + dict_sdblk["blk_wd_last1"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last1"], dict_sdblk["blk_wd_last1"])
                elif i == dict_sdblk["blk_x"] - 1 and j < dict_sdblk["blk_y"] - 1:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:j * dict_sdblk[
                        "blk_ht"] + dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"]:dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"] + dict_sdblk["blk_wd_last1"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd_last1"])
                elif i < dict_sdblk["blk_x"] - 1 and j == dict_sdblk["blk_y"] - 1:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:dict_sdblk["blk_ht_last0"] + (
                            j - 1) * dict_sdblk["blk_ht"] + dict_sdblk["blk_ht_last1"], dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"]:dict_sdblk["blk_wd_last0"] + i * dict_sdblk[
                        "blk_wd"]] = func_sdblk(
                        sdblk_data[j, i, :], dict_sdblk["blk_ht_last1"], dict_sdblk["blk_wd"])
                else:
                    lsc_data[dict_sdblk["blk_ht_last0"] + (j - 1) * dict_sdblk["blk_ht"]:j * dict_sdblk[
                        "blk_ht"] + dict_sdblk["blk_ht_last0"], dict_sdblk["blk_wd_last0"] + (
                            i - 1) * dict_sdblk["blk_wd"]:dict_sdblk["blk_wd_last0"] + i * dict_sdblk[
                        "blk_wd"]] = func_sdblk(sdblk_data[j, i, :], dict_sdblk["blk_ht"], dict_sdblk["blk_wd"])
    try:
        lock.acquire()
        q.put({name: lsc_data})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return lsc_data


def func_sdblk(blk_sdblk_data, blk_ht, blk_wd):
    a = {}
    blk_lsc_data = np.zeros(shape=(blk_ht, blk_wd))
    a[0] = blk_sdblk_data[0] * 2 / blk_wd ** 3 / blk_ht
    a[1] = blk_sdblk_data[1] * 2 / blk_wd / blk_ht ** 3
    a[2] = blk_sdblk_data[2] * 2 / blk_wd ** 3
    a[3] = blk_sdblk_data[3] * 2 / blk_wd ** 2 / blk_ht
    a[4] = blk_sdblk_data[4] * 2 / blk_wd / blk_ht ** 2
    a[5] = blk_sdblk_data[5] * 2 / blk_ht ** 3
    a[6] = blk_sdblk_data[6] * 2 / blk_wd ** 2
    a[7] = blk_sdblk_data[7] * 2 / blk_wd / blk_ht
    a[8] = blk_sdblk_data[8] * 2 / blk_ht ** 2
    a[9] = blk_sdblk_data[9] * 2 / blk_wd
    a[10] = blk_sdblk_data[10] * 2 / blk_ht
    a[11] = blk_sdblk_data[11]
    x = np.array([np.arange(0, blk_wd, 1)])
    y = np.array([np.arange(0, blk_ht, 1)]).T
    """
    for x in range(blk_wd):
        for y in range(blk_ht):
            blk_lsc_data[y, x] = a0 * (x+1) ** 3 * (y+1) + a1 * (x+1) * (y+1) ** 3 + a2 * (x+1) ** 3 + a3 * (
                    x+1) ** 2 * (y+1) + a4 * (x+1) * (y+1) ** 2 + a5 * (y+1) ** 3 + a6 * (x+1) ** 2 + a7 * (
                    x+1) * (y+1) + a8 * (y+1) ** 2 + a9 * (x+1) + a10 * (y+1) + lsc_gain
    """
    blk_lsc_data = cal_sdblk_func(x, y, a)
    return blk_lsc_data


# 定义算法
def cal_sdblk_func(x, y, a):
    return a[0] * (x + 1) ** 3 * (y + 1) + a[1] * (x + 1) * (y + 1) ** 3 + a[2] * (x + 1) ** 3 + a[3] * (
            x + 1) ** 2 * (y + 1) + a[4] * (x + 1) * (y + 1) ** 2 + a[5] * (y + 1) ** 3 + a[6] * (x + 1) ** 2 + a[7] * (
                   x + 1) * (y + 1) + a[8] * (y + 1) ** 2 + a[9] * (x + 1) + a[10] * (y + 1) + a[11]


def lsc_to_csv(image, name):
    # 创建CSV表格数据，内容赋值空
    csv_data = image
    csv_data = csv_data.astype('str')
    np.savetxt(f'Result/{name}.csv', csv_data, delimiter=",", fmt='%s')
    print("输出raw统计数据:", f'{name}.csv')


def do_lsc_for_raw(image, height, width, bayer, sdblk_mask, show_lsc_flag, name):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下对应sdblk文件
    sdblk_file, sdblk_flag = get_sdblk_file(current_working_dir, sdblk_mask)
    if not sdblk_flag:
        # 获取lsc文件
        lsc_file_path, lsc_flag = get_lsc_mask_file(current_working_dir, sdblk_mask)
        if not lsc_flag:
            return image, False
        transform_lsc_data(lsc_file_path)
        sdblk_file = os.path.splitext(lsc_file_path)[0] + ".sdblk"
    print("Sdblk 文件：",sdblk_file)
    R, GR, GB, B = do_pure_raw.bayer_channel_separation(image, bayer)
    # HH, HW = R.shape
    # block_size = 16
    shading_R, shading_GR, shading_GB, shading_B = transf_lsc(sdblk_file, bayer)
    """
    size_new = (HW + block_size, HH + block_size)
    # 插值方法的选择
    ex_R_gain_map = cv2.resize(shading_R, size_new, interpolation=cv2.INTER_CUBIC)
    ex_GR_gain_map = cv2.resize(shading_GR, size_new, interpolation=cv2.INTER_CUBIC)
    ex_GB_gain_map = cv2.resize(shading_GB, size_new, interpolation=cv2.INTER_CUBIC)
    ex_B_gain_map = cv2.resize(shading_B, size_new, interpolation=cv2.INTER_CUBIC)

    half_b_size = block_size // 2
    R_gain_map = ex_R_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GR_gain_map = ex_GR_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GB_gain_map = ex_GB_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    B_gain_map = ex_B_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]

    R_new = R * R_gain_map
    GR_new = GR * GR_gain_map
    GB_new = GB * GB_gain_map
    B_new = B * B_gain_map
    """
    if show_lsc_flag:
        obj = Process(target=raw_image_show.raw_image_show_raw, args=(
            R, GR, GB, B, height // 2, width // 2,
            name + '_no_lsc'))  # args以元组的形式给子进程func函数传位置参数
        obj.start()


    R_new = R * shading_R
    GR_new = GR * shading_GR
    GB_new = GB * shading_GB
    B_new = B * shading_B

    if show_lsc_flag:
        obj = Process(target=raw_image_show.raw_image_show_raw, args=(
            R_new, GR_new, GB_new, B_new, height // 2, width // 2,
            name + '_lsc'))  # args以元组的形式给子进程func函数传位置参数
        obj.start()
    
    new_image = do_pure_raw.bayer_channel_integrration(R_new, GR_new, GB_new, B_new, bayer)
    # new_image = np.clip(new_image, a_min=0, a_max=1023)
    new_image = new_image.astype(np.uint16)
    return new_image, True


if __name__ == "__main__":
    print('This is main of module')
    # hwtbl_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.hwtbl"
    # sdblk_file = "190331773-4433-4436-main-Capture-BFBLD_BASE-LSC.sdblk"
    lsc_file = "044829775-0074-0079-main-Capture-BFBLD_BASE-LSC.lsc"
    # import_exif_hwtbl(hwtbl_file)
    # import_exif_sdblk(sdblk_file)
    # transform_lsc_data()
    # transf_lsc(sdblk_file, 1)
    # transf_lsc(sdblk_file)
    transform_lsc_data(lsc_file)
