#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import numpy as np
from scipy.interpolate import splev, splrep, interp1d
import os
import matplotlib.pyplot as plt


def get_ggm():

    x = [0, 2, 4, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 192, 208, 224, 240, 255]
    y = [0, 3, 13, 26, 63, 89, 108, 124, 137, 149, 160, 177, 191, 202, 211, 219, 226, 237, 242, 247, 251, 255]
    print(x, y)
    return x, y


def do_deggm(img):
    x, y = get_ggm()
    # fun = splrep(x, y, )
    fun = interp1d(y, x, kind="cubic")
    # print(fun)
    x2 = np.arange(0, 2**8, 1)
    y2 = fun(x2)
    # y2 = splev(x2, fun)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x2, y2)
    plt.ion()
    plt.pause(5)
    # plt.show()
    plt.close()
    img = img * 255
    img = fun(img)
    img = img / 255
    return img



if __name__ == "__main__":
    do_deggm(12)
