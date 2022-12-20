#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import numpy as np
import os, shutil, time, sys
import cv2 as cv
import do_pure_raw
import read_unpack_raw as read_unpackraw
from matplotlib import pyplot as plt
import do_sdblk
import demosaic
import multiprocessing
from multiprocessing import Process, Queue, Lock
import do_awb
import do_gtm
import read_packed_word as readpackedword
import raw_image_show
import input_unpacked_raw as inputunpackedraw
from scipy import signal
import exif_parser
import myMutilprocess
import threading
import queue

"""
if __name__ == '__main__':
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        if flag == "Zhong":
            print("################################################################")
            print("Design by Zhongguojun")
            print("Creation time:2022/09/10")
            print("################################################################")
        else:
            flag = int(flag)
    else:
        flag = 0
"""


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 添加输入信息
    print("################################################################")
    flag = input("输入指令:")
    if flag == "Zhong":
        print("################################################################")
        print("Design by Zhongguojun")
        print("Creation time:2022/12/17")
        print("################################################################")
    elif flag == "jinying":
        show_lsc_flag = False
        inputunpackedraw.load_raw(show_lsc_flag)
    elif flag[:-2] == "jinying":
        if flag [-1] == "y":
            print("################################################################")
            print("1、不输入参数------解析：<packed_word>  <lsc>  <jpg>\n")
            print("2、输入参数 1------增加: lsc生成raw图的结果显示\n")
            print("################################################################")
        elif flag [-1] == "1":
            show_lsc_flag = True
            print("################################################################")
            print("输入指令1")
            print("################################################################")
            inputunpackedraw.load_raw(show_lsc_flag)
            
    else:
        print("################################################################")
        print("输入指令错误,退出程序")
        print("################################################################")
        time.sleep(5)
        sys.exit()
    time.sleep(5)

