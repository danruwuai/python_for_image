#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import math,os

def import_exif_hwtbl(hwtbl_file_path):
    width = 4096
    height = 3072

    if width == 0 or height == 0:
        return False
    blk_wd = math.floor(width/(2*16))
    blk_ht = math.floor(height/(2*16))
    blk_wd_last = (width - blk_wd*2*15)/2
    blk_ht_last = (height - blk_ht*2*15)/2
    sdblk_file_path = os.path.splitext(hwtbl_file_path)[0] + ".sdblk"

    with open(hwtbl_file_path, "r") as hwtbl_file:
        with open(sdblk_file_path, "w") as sdblk_file:
            sdblk_file.write( '%9d%9d%9d%9d%9d%9d%9d%9d\n'%(0, 0, blk_wd, blk_ht, 15, 15, blk_wd_last, blk_ht_last))
            for line in hwtbl_file:
                if "blockNum" not in line:
                    data = line.split(", ")[:6]
                    for i in data:
                        sdblk_file.write( "%9d%9d"%(int(i, 16)&0xFFFF, int(i, 16)>>16))
                    sdblk_file.write("\n")       

def import_exif_sdblk(sdblk_file_path):
    """
    blk_wd = math.floor(width/(2*16))
    blk_ht = math.floor(height/(2*16))
    blk_wd_last = (width - blk_wd*2*15)/2
    blk_ht_last = (height - blk_ht*2*15)/2
    """
    hwtbl_file_path = os.path.splitext(sdblk_file_path)[0] + ".hwtbl"

    with open(sdblk_file_path, "r") as sdblk_file:
        with open(hwtbl_file_path, "w") as hwtbl_file:
            lsc_info = sdblk_file.readline()
            print(lsc_info)
            """
            sdblk_file.write( '%9d%9d%9d%9d%9d%9d%9d%9d\n'%(0, 0, blk_wd, blk_ht, 15, 15, blk_wd_last, blk_ht_last))
            for line in hwtbl_file:
                if "blockNum" not in line:
                    data = line.split(", ")[:6]
                    for i in data:
                        sdblk_file.write( "%9d%9d"%(int(i, 16)&0xFFFF, int(i, 16)>>16))
                    sdblk_file.write("\n")   
            """

if __name__ == "__main__":
    print('This is main of module')
    hwtbl_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC2.hwtbl"
    sdblk_file = "093809365-0093-0000-main-MFNR_Before_Blend_LSC21.sdblk"
    import_exif_hwtbl(hwtbl_file)
    import_exif_sdblk(sdblk_file)