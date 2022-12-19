#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3

import raw_image_show as rawshow
import do_pure_raw
import numpy as np


# import math

def read_unpack_file(file_path_name, height, width, bits):
    # 计算位深
    if bits == 8:
        image_bytes = width * height
        frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
        frame.shape = [height, width]
        return frame
    elif bits > 8 & bits <= 16:
        image_bytes = width * height
        frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint16")
        frame.shape = [height, width]
        return frame
    else:
        print("Invalid bits: %d" % bits)
        return False


def test_case_read_unpack():
    #    file_name = "image\Input_4032_3024_RGGB.raw"
    file_name = "Input_unpack_4640x2612_12_2.raw"
    #    done_file_name = "done" + file_name
    image = read_unpack_file(file_name, 2612, 4640, 12)
    #    image = read_mipi10_file(file_name, 3024, 4032)
    #    image = image / 255.0
    image = do_pure_raw.do_black_level_correction(image, 12)
    image = image / 4095.0

    #    rawshow.raw_image_show_thumbnail(image, 3024, 4032)
    rawshow.raw_image_show_thumbnail(image, 2612, 4640)
    rawshow.raw_image_show_fullsize(image, 2612, 4640)
    #    rawshow.raw_image_show_3D(image, 3024, 4032)
    #    rawshow.raw_image_show_fakecolor(image, 3024, 4032, "RGGB")
    rawshow.raw_image_show_fakecolor(image, 2612, 4640, "GRBG")


if __name__ == "__main__":
    print('This is main of module')
    test_case_read_unpack()
