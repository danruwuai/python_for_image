#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import sys
import os
import cv2 as cv
import read_aao


if __name__ == "__main__":
    # 添加输入信息
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
    read_aao.load_aao(flag)
