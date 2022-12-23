#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import os, sys
from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
from multiprocessing import Process
import re, copy
import do_log_filter
import myMutilprocess
import multiprocessing


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 添加输入信息
    print("################################################################")
    if len(sys.argv) > 1:
        config_data = sys.argv[1]
        if config_data == "Zhong":
            print("################################################################")
            print("Design by Zhongguojun")
            print("Creation time:2022/09/10")
            print("################################################################")
    else:
        config_data = 0
    if len(sys.argv) > 2:
        log_path = sys.argv[2]
    else:
        log_path = None
        print("程序正常运行")
        print("################################################################")
    do_log_filter.load_log_file(config_data, log_path)

