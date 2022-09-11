#!/usr/bin/python3
# -*- coding: UTF-8 -*-

def do_black_level_correction(image, bits):
    # 计算OB值，默认64(10 bit)
    image_obc = 16 * 2 ** (bits - 8)
    image[image < image_obc] = image_obc
    image = image - image_obc

    return image
