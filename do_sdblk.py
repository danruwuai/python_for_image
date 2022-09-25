#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import os
import numpy as np



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
                    for i in range(0, 6):
                        hwtbl_file.write("0x%08x, " % (int(data[i * 2 * data_num: (i * 2 + 1) * data_num]) + (int(data[(i * 2+ 1) * data_num: (i * 2 + 2) * data_num]) << 16)))
                    hwtbl_file.write("\n")


def transform_lsc_data(lsc_file_path):
    hwtbl_file_path = os.path.splitext(lsc_file_path)[0].split("_LSC2")[0] + ".hwtbl"
    sdblk_file_path = os.path.splitext(lsc_file_path)[0].split("_LSC2")[0] + ".sdblk"
    print(hwtbl_file_path, sdblk_file_path)
    with open(lsc_file_path, "rb") as lsc_file:
        with open(hwtbl_file_path, "w") as hwtbl_file:
            with open(sdblk_file_path, "w") as sdblk_file:
                i = 0
                sum = hex(0)
                if 1:
                    c = lsc_file.read(1)
                    a = hex(ord(c))
                    y = 2
                    a = a
                    print(a)
                    i = i + 1
                    if not c:
                        1
                    x, y = divmod(i, 4)

                    if i % 4 == 0:
                        hwtbl_file.write(sum)
                        sum = hex(0)





if __name__ == "__main__":
    print('This is main of module')
    # hwtbl_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.hwtbl"
    # sdblk_file = "Capture20190711-075546ISOAuto.sdblk"
    lsc_file = "Capture20190711-075546ISOAuto_LSC2.lsc"
    # import_exif_hwtbl(hwtbl_file)
    # import_exif_sdblk(sdblk_file)
    transform_lsc_data(lsc_file)
