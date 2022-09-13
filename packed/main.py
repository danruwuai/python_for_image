#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import input_packed_word
import numpy as np
import sys
import os
import math
import cv2 as cv
import read_packed_word as readpackedword

if __name__ == '__main__':
    # 添加输入信息
    if len(sys.argv) > 1:
        author = sys.argv[1]
        if author == "Zhong":
            print("________________________________________________________________")
            print("Design by Zhongguojun")
            print("Creation time:2022/09/10")
            print("________________________________________________________________")
    input_packed_word.input_pack_word()