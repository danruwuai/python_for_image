#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt

def get_lsc_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("lsc") and os.path.isfile(file)))

    return file_list

def get_sdblk_file(dir_path, sdblk_mask):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        for file in files:
            if (file.endswith("sdblk") and os.path.isfile(file)) and file[:19] == sdblk_mask:
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
                        hwtbl_file.write("0x%08x, " % (lsc_file[i + 21] + (int(lsc_file[izeros + 22]) << 16)))
                    if i % 12 == 11:
                        sdblk_file.write('\n')
                        hwtbl_file.write("\n")
                


def transf_lsc(sdblk_file_path, bayer):
    sdblk_name = os.path.splitext(sdblk_file_path)[0]
    data_num = 9
    with open(sdblk_file_path, "r") as sdblk_file:       
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
        blk_y = blk_num_y + 1
        blk_x = blk_num_x + 1
        lsc_data_0 = np.zeros(shape = (blk_y * 3, blk_x * 4))
        lsc_data_1 = np.zeros(shape = (blk_y * 3, blk_x * 4))
        lsc_data_2 = np.zeros(shape = (blk_y * 3, blk_x * 4))
        lsc_data_3 = np.zeros(shape = (blk_y * 3, blk_x * 4))
        flag = 0
        # next(sdblk_file)
        for line in sdblk_file:
            if "blockNum" not in line:
                data_all = line.split("\n")
                data = data_all[0]
                for i in range(12):
                    if(flag % 4 == 0):
                        data[i * data_num: (i + 1) * data_num]
                        if i == 11:
                            lsc_data_0[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                        elif(int(data[i * data_num: (i + 1) * data_num]) >= 32768):
                            lsc_data_0[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(32768 - int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                        else:
                            lsc_data_0[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = (int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                    elif(flag % 4 == 1):
                        if i == 11:
                            lsc_data_1[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                        elif(int(data[i * data_num: (i + 1) * data_num]) >= 32768):
                            lsc_data_1[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(32768 - int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                        else:
                            lsc_data_1[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = (int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                    elif(flag % 4 == 2):
                        if i == 11:
                            lsc_data_2[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                        elif(int(data[i * data_num: (i + 1) * data_num]) >= 32768):
                            lsc_data_2[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(32768 - int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                        else:
                            lsc_data_2[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = (int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                    elif(flag % 4 == 3):
                        if i == 11:
                            lsc_data_3[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(data[i * data_num: (i + 1) * data_num]) / 4096
                        elif(int(data[i * data_num: (i + 1) * data_num]) >= 32768):
                            lsc_data_3[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = int(32768 - int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                        else:
                            lsc_data_3[3 * (flag // (4 * blk_x)) + i // 4, 4 * (flag // 4 % blk_x) + i % 4] = (int(data[i * data_num: (i + 1) * data_num]) + int(data[11 * data_num: (11 + 1) * data_num])) / 4096
                flag = flag + 1
                        
        ax = plt.subplot(1, 1, 1, projection='3d')
        X = np.arange(0, blk_x * 4)
        Y = np.arange(0, blk_y * 3)
        X, Y = np.meshgrid(X, Y)
        # R = np.sqrt(X ** 2 + Y ** 2)
        # 具体函数方法可用help(function)查看，如：help（ax.plot_surface)
        # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
        ax.plot_wireframe(X, Y, lsc_data_0, rstride=1, cstride=1)
        plt.show()
        print('show')            
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



def lsc_to_csv(image, name):
    # 创建CSV表格数据，内容赋值空
    csv_data = image
    csv_data = csv_data.astype('str')
    np.savetxt(f'{name}.csv', csv_data, delimiter=",", fmt='%s')
    print("输出raw统计数据:", f'{name}.csv')


def do_lsc_for_raw(image, image_height, image_width, bayer, sdblk_mask):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下对应sdblk文件
    sdblk_file, sdblk_flag = get_sdblk_file(current_working_dir,sdblk_mask)
    if sdblk_flag == False:
        return image, False
    R, GR, GB, B = bayer_channel_separation(image, bayer)
    HH, HW = R.shape
    block_size = 16
    shading_R, shading_GR, shading_GB, shading_B = transf_lsc(sdblk_file, bayer)
    size_new = (HW + block_size, HH + block_size)
    # 插值方法的选择
    ex_R_gain_map = cv2.resize(shading_R, size_new, interpolation = cv2.INTER_CUBIC)
    ex_GR_gain_map = cv2.resize(shading_GR, size_new, interpolation = cv2.INTER_CUBIC)
    ex_GB_gain_map = cv2.resize(shading_GB, size_new, interpolation = cv2.INTER_CUBIC)
    ex_B_gain_map = cv2.resize(shading_B, size_new, interpolation = cv2.INTER_CUBIC)
    
    half_b_size = int(block_size / 2)
    R_gain_map = ex_R_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GR_gain_map = ex_GR_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GB_gain_map = ex_GB_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    B_gain_map = ex_B_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    
    R_new = R * R_gain_map
    GR_new = GR * GR_gain_map
    GB_new = GB * GB_gain_map
    B_new = B * B_gain_map
    
    new_image = bayer_channel_integration(R_new, GR_new, GB_new, B_new, image_height, image_width, bayer)
    new_image = np.clip(new_image, a_min = 0, a_max = 1023)
    return new_image, True


def bayer_channel_separation(file_name, bayer):
    R = file_name[:, :, 0]
    GR = file_name[:, :, 1]
    GB = file_name[:, :, 2]
    B = file_name[:, :, 3]
    # 0:B 1:GB 2:GR 3:R
    if bayer in [3, "RGGB"]:
        R = file_name[:, :, 0]
        GR = file_name[:, :, 1]
        GB = file_name[:, :, 2]
        B = file_name[:, :, 3]
    elif bayer in [2, "GRBG"]:
        GR = file_name[:, :, 0]
        R = file_name[:, :, 1]
        B = file_name[:, :, 2]
        GB = file_name[:, :, 3]
    elif bayer in [1, "GBRG"]:
        GB = file_name[:, :, 0]
        B = file_name[:, :, 1]
        R = file_name[:, :, 2]
        GR = file_name[:, :, 3]
    elif bayer in [0, "BGGR"]:
        B = file_name[:, :, 0]
        GB = file_name[:, :, 1]
        GR = file_name[:, :, 2]
        R = file_name[:, :, 3]
    else:
        print("no match bayer")
        return False
    return R, GR, GB, B

def bayer_channel_integration(R, GR, GB, B, height, width, bayer):
    rgb_img = np.zeros(shape=(height, width, 4))
    # 0:B 1:GB 2:GR 3:R
    if bayer in [3, "RGGB"]:
        rgb_img[:, :, 0] = R
        rgb_img[:, :, 1] = GR
        rgb_img[:, :, 2] = GB
        rgb_img[:, :, 3] = B
    elif bayer in [2, "GRBG"]:
        rgb_img[:, :, 0] = GR
        rgb_img[:, :, 1] = R
        rgb_img[:, :, 2] = B
        rgb_img[:, :, 3] = GB
    elif bayer in [1, "GBRG"]:
        rgb_img[:, :, 0] = GB
        rgb_img[:, :, 1] = B
        rgb_img[:, :, 2] = R
        rgb_img[:, :, 3] = GR
    elif bayer in [0, "BGGR"]:
        rgb_img[:, :, 0] = B
        rgb_img[:, :, 1] = GB
        rgb_img[:, :, 2] = GR
        rgb_img[:, :, 3] = R
    else:
        print("no match bayer")
        return False
    return rgb_img

if __name__ == "__main__":
    print('This is main of module')
    # hwtbl_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.hwtbl"
    sdblk_file = "000127703-0302-0000-main-MFNR_Before_Blend.sdblk"
    #lsc_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.lsc"
    # import_exif_hwtbl(hwtbl_file)
    # import_exif_sdblk(sdblk_file)
    # transform_lsc_data()
    transf_lsc(sdblk_file)