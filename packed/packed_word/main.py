#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import input_packed_word
import numpy as np
import sys
import os,time
import math
import cv2 as cv
import read_aao as aao
import read_packed_word as readpackedword
import input_unpacked_raw
import do_pure_raw
import read_unpack_raw as read_unpackraw

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
    # 添加输入信息
    print("################################################################")
    flag = input("输入指令:")
    if flag == "Zhong":
        print("################################################################")
        print("Design by Zhongguojun")
        print("Creation time:2022/09/22")
        print("################################################################")
    elif flag == "jinying":
        csv_flag = 0
        aao.load_aao(csv_flag)
        input_packed_word.input_pack_word()
        input_packed_word.input_lsc_raw()
        input_packed_word.input_pack_word_s0()
    elif flag[:-2] == "jinying":
        if flag [-1] == "y":
            print("################################################################")
            print("1、不输入参数------解析：<packed_word>  <aao>  <lsc_16bit>\n")
            print("2、输入参数 1------解析：<packed_word>  <aao+高低位统计图>  <lsc_16bit>\n")
            print("3、输入参数 2------解析：<packed_word>  <aao+高低位统计图+csv数据>  <lsc_16bit>\n")
            print("4、输入参数 3------解析：<unpack_raw>\n")
            print("################################################################")
        elif flag [-1] == "3":
            input_unpacked_raw.load_raw()
        elif flag[-1] in ["1", "2"]:
            csv_flag = int(flag[-1])
            aao.load_aao(csv_flag)
            input_packed_word.input_pack_word()
            input_packed_word.input_lsc_raw()
            input_packed_word.input_pack_word_s0()
        else:
            csv_flag = 0
            aao.load_aao(csv_flag)
            input_packed_word.input_pack_word()
            input_packed_word.input_lsc_raw()
            input_packed_word.input_pack_word_s0()
    else:
        print("################################################################")
        print("输入指令错误,退出程序")
        print("################################################################")
        time.sleep(5)
        sys.exit()
    time.sleep(5)

