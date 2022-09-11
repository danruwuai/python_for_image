#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import raw_image_show as rawshow
import numpy as np
import math


def read_mipi10_file(file_path_name, height, width):
    # 当行长度补齐
    new_width = int(math.floor((width + 3) / 4) * 4)  # 对四字节补齐
    packet_num_L = int(new_width / 4)
    width_byte_num = packet_num_L * 5  # 当行byte长度
    width_byte_num = int(math.floor((width_byte_num + 7) / 8) * 8)  # 当行对8字节补齐
    image_bytes = width_byte_num * height
    Align_num = width_byte_num % 5
    frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
    print("b shape", frame.shape)
    print('%#x' % frame[0])
    frame.shape = [height, width_byte_num]  # 高字节整理图像矩阵
    one_byte = frame[:, 0:image_bytes:5]
    two_byte = frame[:, 1:image_bytes:5]
    three_byte = frame[:, 2:image_bytes:5]
    four_byte = frame[:, 3:image_bytes:5]
    five_byte = frame[:, 4:image_bytes:5]
    if Align_num == 1:
        two_byte = np.column_stack((two_byte, np.arange(1, height + 1)))
        three_byte = np.column_stack((three_byte, np.arange(1, height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, height + 1)))
        print('Aligh is 1')
    elif Align_num == 2:
        three_byte = np.column_stack((three_byte, np.arange(1, height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, height + 1)))
        print('Aligh is 2')
    elif Align_num == 3:
        four_byte = np.column_stack((four_byte, np.arange(1, height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, height + 1)))
        print('Aligh is 3')
    elif Align_num == 4:
        five_byte = np.column_stack((five_byte, np.arange(1, height + 1)))
        print('Aligh is 4')
    else:
        print('That is not to Aligh')
    # 数据转换防止溢出
    one_byte = one_byte.astype('uint16')
    two_byte = two_byte.astype('uint16')
    three_byte = three_byte.astype('uint16')
    four_byte = four_byte.astype('uint16')
    five_byte = five_byte.astype('uint16')
    # 用矩阵的方法进行像素的拼接
    one_byte = np.left_shift(one_byte, 2) + np.bitwise_and((five_byte), 3)
    two_byte = np.left_shift(two_byte, 2) + np.right_shift(np.bitwise_and((five_byte), 12), 2)
    three_byte = np.left_shift(three_byte, 2) + np.right_shift(np.bitwise_and((five_byte), 48), 4)
    four_byte = np.left_shift(four_byte, 2) + np.right_shift(np.bitwise_and((five_byte), 192), 6)

    frame_pixels = np.zeros(shape=(height, new_width))
    frame_pixels[:, 0: new_width:4] = one_byte[:, 0: packet_num_L]
    frame_pixels[:, 1: new_width:4] = two_byte[:, 0: packet_num_L]
    frame_pixels[:, 2: new_width:4] = three_byte[:, 0: packet_num_L]
    frame_pixels[:, 3: new_width:4] = four_byte[:, 0: packet_num_L]
    # 裁剪无用的数据
    frame_out = frame_pixels[:, 0:width]
    return frame_out


def test_case_read_mipi_10():
    #    file_name = "image\Input_4032_3024_RGGB.raw"
    #    file_name = "CWF-MCC.raw"
    file_name = "101907391-0060-0060-main-P1-IMGO-PW4672-PH2612-BW5840__4640x2612_10_2.packed_wordunpack.raw"
    #    done_file_name = "done"+file_name
    #    image = read_mipi10_file(file_name,1728,2304)
    image = read_mipi10_file(file_name, 2612, 4640)
    # image = read_mipi10_file(file_name,3024,4032)
    # image = image/255.0
    image = image / 1023.0

    rawshow.raw_image_show_thumbnail(image, 2612, 4640)


#    rawshow.raw_image_show_thumbnail(image, 1728, 2304)
# rawshow.raw_image_show_fullsize(image,3024,4032)
# rawshow.raw_image_show_3D(image,3024,4032)
# rawshow.raw_image_show_fakecolor(image,3024,4032,"RGGB")
#    rawshow.raw_image_show_fakecolor(image,1728,2304,"GRBG")


if __name__ == "__main__":
    print('This is main of module')
    test_case_read_mipi_10()

