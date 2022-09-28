#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import os
import numpy as np

def get_lsc_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("lsc") and os.path.isfile(file)))

    return file_list

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
                        hwtbl_file.write("0x%08x, " % (int(data[i * 2 * data_num: (i * 2 + 1) * data_num]) + (int(data[(i * 2 + 1) * data_num: (i * 2 + 2) * data_num]) << 16)))
                    hwtbl_file.write("\n")


def transform_lsc_data():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_lsc_list = get_lsc_file(current_working_dir)
    # print(file_raw_list)
    # 循环查找raw的文件
    for lsc_file_path in file_lsc_list:
        print("获取的文件：", lsc_file_path)
        hwtbl_file_path = os.path.splitext(lsc_file_path)[0] + ".hwtbl"
        sdblk_file_path = os.path.splitext(lsc_file_path)[0] + ".sdblk"
        print(hwtbl_file_path, sdblk_file_path)
        with open(hwtbl_file_path, "w") as hwtbl_file:
            with open(sdblk_file_path, "w") as sdblk_file:
                lsc_size = os.path.getsize(lsc_file_path)
                print(lsc_size)
                lsc_file = np.fromfile(lsc_file_path, count=lsc_size, dtype="uint16")
                width = lsc_file[0] + np.left_shift(lsc_file[1],8)
                height = lsc_file[2] + np.left_shift(lsc_file[3],8)
                blk_num_w = lsc_file[4] + np.left_shift(lsc_file[5],8)
                blk_num_h = lsc_file[6] + np.left_shift(lsc_file[7],8)           
                blk_num_x = lsc_file[8] + np.left_shift(lsc_file[9],8)
                blk_num_y = lsc_file[10] + np.left_shift(lsc_file[11],8)
                blk_wd = lsc_file[12] + np.left_shift(lsc_file[13],8)
                blk_ht = lsc_file[14] + np.left_shift(lsc_file[15],8) 
                blk_wd_last = lsc_file[16] + np.left_shift(lsc_file[17],8)
                blk_ht_last = lsc_file[18] + np.left_shift(lsc_file[19],8)
                unknown = lsc_file[20] + np.left_shift(lsc_file[21],8)
                print(width, height, blk_num_w, blk_num_h, blk_num_x, blk_num_y, blk_wd, blk_ht, blk_wd_last, blk_ht_last, unknown)      
                sdblk_file.write('%9d%9d%9d%9d%9d%9d%9d%9d\n' % (0, 0, blk_wd, blk_ht, blk_num_x, blk_num_y, blk_wd_last, blk_ht_last))
                for i in range((blk_num_w - 1)*(blk_num_h - 1) * 4 * 12):
                    sdblk_file.write('%9d' % (lsc_file[i + 22]))
                    if i % 2 == 1:
                        hwtbl_file.write("0x%08x, " % (lsc_file[i + 21] + (int(lsc_file[i + 22]) << 16)))
                    if i % 12 == 11:
                        sdblk_file.write('\n')
                        hwtbl_file.write("\n")
                

if __name__ == "__main__":
    print('This is main of module')
    # hwtbl_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.hwtbl"
    # sdblk_file = "Capture20190711-075546ISOAuto.sdblk"
    #lsc_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.lsc"
    # import_exif_hwtbl(hwtbl_file)
    # import_exif_sdblk(sdblk_file)
    transform_lsc_data()
