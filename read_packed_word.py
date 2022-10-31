#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import raw_image_show as rawshow
import numpy as np
import math
import os
import cv2 as cv
from matplotlib import pyplot as plt
import do_pure_raw


# 读取packed_word信息，返回数据和raw_name,准确的width
def read_packed_word(file_path_name, height, width, bayer, bit):
    yuv_flag = 0
    if bit == 12:
        frame_out = read_packed_word_12(file_path_name, height, width)
        if frame_out is False:
            return False, False, False, False
    else:
        # 调用函数获取实际width
        new_width, width_real, width_byte_num, packet_num_L, width_flag = get_width_real(file_path_name, height, width)
        print("width_flag:", width_flag)
        # 求对应的商和余值
        packet_num_L, Align_num = divmod(width_byte_num, 5)
        image_bytes = width_byte_num * height  # 获取图片真实的大小
        frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
        print("b shape", frame.shape)
        print('%#x' % frame[0])
        frame.shape = [height, width_byte_num]  # 高字节整理图像矩阵
        # 5字节读取数据
        one_byte = frame[:, 0:image_bytes:5]
        two_byte = frame[:, 1:image_bytes:5]
        three_byte = frame[:, 2:image_bytes:5]
        four_byte = frame[:, 3:image_bytes:5]
        five_byte = frame[:, 4:image_bytes:5]
        # 计算补偿的0值
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
        one_byte = np.left_shift(np.bitwise_and(two_byte, 3), 10) + np.left_shift(one_byte, 2)
        two_byte = np.bitwise_and(two_byte, 252) + np.left_shift(np.bitwise_and(three_byte, 15), 8)
        three_byte = np.right_shift(np.bitwise_and(three_byte, 240), 2) + np.left_shift(np.bitwise_and(four_byte, 63),
                                                                                        6)
        four_byte = np.right_shift(np.bitwise_and(four_byte, 192), 4) + np.left_shift(five_byte, 4)
        # 整合各通道数据到一起
        frame_pixels = np.zeros(shape=(height, new_width))
        frame_pixels[:, 0:new_width:4] = one_byte[:, 0:packet_num_L]
        frame_pixels[:, 1:new_width:4] = two_byte[:, 0:packet_num_L]
        frame_pixels[:, 2:new_width:4] = three_byte[:, 0:packet_num_L]
        frame_pixels[:, 3:new_width:4] = four_byte[:, 0:packet_num_L]
        # 裁剪无用的数据
        frame_out = frame_pixels[:, 0:width_real]
        # 替换10 bit为12 bit
        raw_name = file_path_name[:-12]
        raw_name = raw_name.replace('_10_', '_12_')
        # 判断width是否正确
        if width_flag == 1:
            print("Wrong width,Calculated real width ")
            new_width_real = width_real
            for i in range(new_width_real - 32, new_width_real):  # 在末尾32字节范围内判断
                if frame_out[0, i] == 0:  # 判断为0的补偿值
                    if frame_out[int(height / 2), i] == 0:  # 判断为0的补偿值
                        if i < new_width_real:
                            new_width_real = i
                            print("new_width_real = ", new_width_real)
            frame_out = frame_out[:, 0:new_width_real]  # 裁剪无用数据
            if new_width_real == width * 1.5:

                frame_y = np.zeros(shape=(height, width))
                uv_width = width // 4
                frame_cb = np.zeros(shape=(height, uv_width))
                frame_cr = np.zeros(shape=(height, uv_width))
                frame_y[:, 0:width:4] = frame_out[:, 0:new_width_real:6]
                frame_y[:, 1:width:4] = frame_out[:, 2:new_width_real:6]
                frame_y[:, 2:width:4] = frame_out[:, 3:new_width_real:6]
                frame_y[:, 3:width:4] = frame_out[:, 5:new_width_real:6]
                yuv_flag = 1
                """
                frame_cb[:, :] = frame_out[:, 1:new_width_real:6]
                frame_cr[:, :] = frame_out[:, 4:new_width_real:6]
                Cb = frame_cb.repeat(4, 1)
                Cr = frame_cr.repeat(4, 1)
                raw_cb = Cb / 16
                raw_cb = raw_cb.astype(np.uint8)
                cv.imwrite(raw_name + '.bmp', cv.cvtColor(raw_cb, cv.COLOR_RGBA2BGRA))
                raw_name = raw_name.replace('_12_', '_8_')
                frame_ycbcr = do_ycbcr(frame_y, Cb, Cr, height, width, raw_name)
                # frame_out = frame_yuv
                # frame_out = frame_out[:, 0:width]
                # new_width_real = width

                # rgb_img = read_yuv_packed_word(frame_out, height, width)
                """
                return frame_y, raw_name, width, yuv_flag

            raw_name = raw_name.replace(f'_{width}x', f'_{new_width_real}x')  # 更换实际的width
            print("raw_name = ", raw_name)
            width = new_width_real
    raw_byte = frame_out
    # 转换为8bit，输出对应raw数据
    frame_raw_low = np.uint8(raw_byte)  # 低8位获取
    raw_byte = raw_byte.astype('uint16')
    raw_byte = np.right_shift(raw_byte, 8)
    frame_raw_high = raw_byte  # 高8位获取
    raw_width = width * 2  # unpack_raw,直接排列
    frame_raw = np.zeros(shape=(height, raw_width))
    frame_raw[:, 0:raw_width:2] = frame_raw_low
    frame_raw[:, 1:raw_width:2] = frame_raw_high
    frame_raw = frame_raw.astype('uint8')
    # 写入raw文件
    frame_raw.tofile(raw_name + ".raw")
    # 根据bayer转换raw
    rgb_img = np.zeros(shape=(height, width, 3))
    R = rgb_img[:, :, 0]
    GR = rgb_img[:, :, 1]
    GB = rgb_img[:, :, 1]
    B = rgb_img[:, :, 2]
    # 0:B 1:GB 2:GR 3:R
    if bayer == 3:
        R[::2, ::2] = frame_out[::2, ::2]
        GR[::2, 1::2] = frame_out[::2, 1::2]
        GB[1::2, ::2] = frame_out[1::2, ::2]
        B[1::2, 1::2] = frame_out[1::2, 1::2]
    elif bayer == 2:
        GR[::2, ::2] = frame_out[::2, ::2]
        R[::2, 1::2] = frame_out[::2, 1::2]
        B[1::2, ::2] = frame_out[1::2, ::2]
        GB[1::2, 1::2] = frame_out[1::2, 1::2]
    elif bayer == 1:
        GB[::2, ::2] = frame_out[::2, ::2]
        B[::2, 1::2] = frame_out[::2, 1::2]
        R[1::2, ::2] = frame_out[1::2, ::2]
        GR[1::2, 1::2] = frame_out[1::2, 1::2]
    elif bayer == 0:
        B[::2, ::2] = frame_out[::2, ::2]
        GB[::2, 1::2] = frame_out[::2, 1::2]
        GR[1::2, ::2] = frame_out[1::2, ::2]
        R[1::2, 1::2] = frame_out[1::2, 1::2]
    else:
        print("no match bayer")
        return frame_out, raw_name, width, yuv_flag
    return rgb_img, raw_name, width, yuv_flag


# 读取lsc_raw信息，返回数据和raw_name
def read_lsc_raw(file_path_name, height, width, bayer):

    image_bytes = width * height  # 获取图片真实的大小
    frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint32")
    print("b shape", frame.shape)
    print('%#x' % frame[0])
    frame.shape = [height, width]  # 高字节整理图像矩阵
    frame = frame.astype('uint16')
    # 替换16 bit为12 bit
    raw_name = file_path_name[:-4]
    raw_name = raw_name.replace('_16_', '_12_')
    """
    raw_byte = frame
    # 转换为8bit,输出对应raw数据
    frame_raw_low = np.uint8(raw_byte)  # 低8位获取
    raw_byte = raw_byte.astype('uint16')
    raw_byte = np.right_shift(raw_byte, 8)
    frame_raw_high = raw_byte  # 高8位获取
    frame_raw = np.zeros(shape=(height, width))
    frame_raw[:, 0:width:2] = frame_raw_low
    frame_raw[:, 1:width:2] = frame_raw_high
    frame_raw = frame_raw.astype('uint8')
    """
    # 写入raw文件
    frame.tofile(raw_name + ".raw")
    if 0:
        # 输出csv数据
        do_pure_raw.raw_to_csv(frame, height, width, bayer, raw_name)
    # 根据bayer转换raw
    rgb_img = np.zeros(shape=(height, width, 3))
    R = rgb_img[:, :, 0]
    GR = rgb_img[:, :, 1]
    GB = rgb_img[:, :, 1]
    B = rgb_img[:, :, 2]
    # 0:B 1:GB 2:GR 3:R
    if bayer == 3:
        R[::2, ::2] = frame[::2, ::2]
        GR[::2, 1::2] = frame[::2, 1::2]
        GB[1::2, ::2] = frame[1::2, ::2]
        B[1::2, 1::2] = frame[1::2, 1::2]
    elif bayer == 2:
        GR[::2, ::2] = frame[::2, ::2]
        R[::2, 1::2] = frame[::2, 1::2]
        B[1::2, ::2] = frame[1::2, ::2]
        GB[1::2, 1::2] = frame[1::2, 1::2]
    elif bayer == 1:
        GB[::2, ::2] = frame[::2, ::2]
        B[::2, 1::2] = frame[::2, 1::2]
        R[1::2, ::2] = frame[1::2, ::2]
        GR[1::2, 1::2] = frame[1::2, 1::2]
    elif bayer == 0:
        B[::2, ::2] = frame[::2, ::2]
        GB[::2, 1::2] = frame[::2, 1::2]
        GR[1::2, ::2] = frame[1::2, ::2]
        R[1::2, 1::2] = frame[1::2, 1::2]
    else:
        print("no match bayer")
        return frame, raw_name
    """
    np.savetxt('R.csv', R, delimiter=",", fmt='%s')
    np.savetxt('GR.csv', GR, delimiter=",", fmt='%s')
    np.savetxt('GB.csv', GB, delimiter=",", fmt='%s')
    np.savetxt('B.csv', B, delimiter=",", fmt='%s')
    """
    return rgb_img, raw_name


# get_width_real获取数据，同时输出可能的width_real
def get_width_real(file_path_name, height, width):
    # 获取文件大小
    file_num = os.path.getsize(file_path_name)
    print("file_num: ", file_num)
    # 计算width实际数据
    width_byte_real = int(file_num / height)
    print("width_real: ", width_byte_real)
    # 当行长度补齐
    new_width = int(math.floor((width + 3) / 4) * 4)  # 对4字节补齐
    # new_width_32 = int(math.floor((new_width + 31) / 32) * 32)  # 对32字节补齐
    packet_num_L = new_width // 4
    width_byte_num = packet_num_L * 5  # 当行byte长度
    width_byte_num = int(math.floor((width_byte_num + 7) / 8) * 8)  # 当行对8字节补齐
    # 判断是否width正确
    width_flag = 0
    if width_byte_num == width_byte_real:
        return new_width, width, width_byte_num, packet_num_L, width_flag
    else:  # 上边的条件都不满足，计算最大的width值输出
        packet_num_L, width_align = divmod(width_byte_real, 5)
        width_real = packet_num_L * 4
        width_flag = 1
        return width_real, width_real, width_byte_real, packet_num_L, width_flag


# 读取packed_word_yplane信息，返回数据和raw_name,准确的width
def read_packed_word_yplane(file_path_name, height, width, bit, ph_height, pw_width, bw_width):
    if bit == 12:
        frame_out = read_packed_word_12(file_path_name, height, width, ph_height, pw_width, bw_width)
        raw_name = file_path_name[:-12]
        if frame_out is False:
            return False, False, False
    else:
        if ph_height == -1 and pw_width == -1 and bw_width == -1:
            # 调用函数获取实际width
            new_width, width_real, width_byte_num, packet_num_L, width_flag = get_width_real(file_path_name, height, width)
            print("width_flag:", width_flag)
            # 求对应的商和余值
            packet_num_L, Align_num = divmod(width_byte_num, 5)
            image_bytes = width_byte_num * height  # 获取图片真实的大小
            frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
            print("b shape", frame.shape)
            print('%#x' % frame[0])
            frame.shape = [height, width_byte_num]  # 高字节整理图像矩阵
            # 5字节读取数据
            one_byte = frame[:, 0:image_bytes:5]
            two_byte = frame[:, 1:image_bytes:5]
            three_byte = frame[:, 2:image_bytes:5]
            four_byte = frame[:, 3:image_bytes:5]
            five_byte = frame[:, 4:image_bytes:5]
            # 计算补偿的0值
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
            one_byte = np.left_shift(np.bitwise_and(two_byte, 3), 10) + np.left_shift(one_byte, 2)
            two_byte = np.bitwise_and(two_byte, 252) + np.left_shift(np.bitwise_and(three_byte, 15), 8)
            three_byte = np.right_shift(np.bitwise_and(three_byte, 240), 2) + np.left_shift(np.bitwise_and(four_byte, 63),
                                                                                            6)
            four_byte = np.right_shift(np.bitwise_and(four_byte, 192), 4) + np.left_shift(five_byte, 4)
            # 整合各通道数据到一起
            frame_pixels = np.zeros(shape=(height, new_width))
            frame_pixels[:, 0:new_width:4] = one_byte[:, 0:packet_num_L]
            frame_pixels[:, 1:new_width:4] = two_byte[:, 0:packet_num_L]
            frame_pixels[:, 2:new_width:4] = three_byte[:, 0:packet_num_L]
            frame_pixels[:, 3:new_width:4] = four_byte[:, 0:packet_num_L]
            # 裁剪无用的数据
            frame_out = frame_pixels[:, 0:width_real]
            # 替换10 bit为12 bit
            raw_name = file_path_name[:-12]
            raw_name = raw_name.replace('_10_', '_12_')
            # 判断width是否正确
            if width_flag == 1:
                print("Wrong width,Calculated real width ")
                new_width_real = width_real
                for i in range(width_real - 32, width_real):  # 在末尾32字节范围内判断
                    if frame_out[0, i] == 0:  # 判断为0的补偿值
                        if frame_out[int(height / 2), i] == 0:  # 判断为0的补偿值
                            if i < new_width_real:
                                new_width_real = i
                                print("new_width_real = ", new_width_real)
                frame_out = frame_out[:, 0:new_width_real]  # 裁剪无用数据
                raw_name = raw_name.replace(f'_{width}x', f'_{new_width_real}x')  # 更换实际的width
                print("raw_name = ", raw_name)
                width = new_width_real
        else:
            frame_out = transf_packed_to_raw(file_path_name, height, width, ph_height, pw_width, bw_width)
            # 替换10 bit为12 bit
            raw_name = file_path_name[:-12]
            raw_name = raw_name.replace('_10_', '_12_')
    return frame_out, raw_name, width


# 读取packed_word_cplane信息，返回数据和raw_name,准确的width
def read_packed_word_cplane(file_path_name, height, width, bit, ph_height, pw_width, bw_width):
    if bit == 12:
        frame_out = read_packed_word_cplane_12(file_path_name, height, width, ph_height, pw_width, bw_width)
        raw_name = file_path_name[:-12]
        if frame_out is False:
            return False, False, False, False
    else:
        if ph_height == -1 and pw_width == -1 and bw_width == -1:
            # 调用函数获取实际width
            new_width, width_real, width_byte_num, packet_num_L, width_flag = get_width_real(file_path_name, height, width)
            print("width_flag:", width_flag)
            # 求对应的商和余值
            packet_num_L, Align_num = divmod(width_byte_num, 5)
            image_bytes = width_byte_num * height  # 获取图片真实的大小
            frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
            print("b shape", frame.shape)
            print('%#x' % frame[0])
            frame.shape = [height, width_byte_num]  # 高字节整理图像矩阵
            # 5字节读取数据
            one_byte = frame[:, 0:image_bytes:5]
            two_byte = frame[:, 1:image_bytes:5]
            three_byte = frame[:, 2:image_bytes:5]
            four_byte = frame[:, 3:image_bytes:5]
            five_byte = frame[:, 4:image_bytes:5]
            # 计算补偿的0值
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
            one_byte = np.left_shift(np.bitwise_and(two_byte, 3), 10) + np.left_shift(one_byte, 2)
            two_byte = np.bitwise_and(two_byte, 252) + np.left_shift(np.bitwise_and(three_byte, 15), 8)
            three_byte = np.right_shift(np.bitwise_and(three_byte, 240), 2) + np.left_shift(np.bitwise_and(four_byte, 63),
                                                                                            6)
            four_byte = np.right_shift(np.bitwise_and(four_byte, 192), 4) + np.left_shift(five_byte, 4)
            # 整合各通道数据到一起
            frame_pixels = np.zeros(shape=(height, new_width))
            frame_pixels[:, 0:new_width:4] = one_byte[:, 0:packet_num_L]
            frame_pixels[:, 1:new_width:4] = two_byte[:, 0:packet_num_L]
            frame_pixels[:, 2:new_width:4] = three_byte[:, 0:packet_num_L]
            frame_pixels[:, 3:new_width:4] = four_byte[:, 0:packet_num_L]
            # 裁剪无用的数据
            frame_out = frame_pixels[:, 0:width_real]
            # 替换10 bit为12 bit
            raw_name = file_path_name[:-12]
            raw_name = raw_name.replace('_10_', '_12_')
            # 判断width是否正确
            if width_flag == 1:
                print("Wrong width,Calculated real width ")
                new_width_real = width_real
                for i in range(width_real - 32, width_real):  # 在末尾32字节范围内判断
                    if frame_out[0, i] == 0:  # 判断为0的补偿值
                        if frame_out[int(height / 2), i] == 0:  # 判断为0的补偿值
                            if i < new_width_real:
                                new_width_real = i
                                print("new_width_real = ", new_width_real)
                frame_out = frame_out[:, 0:new_width_real]  # 裁剪无用数据
                raw_name = raw_name.replace(f'_{width}x', f'_{new_width_real}x')  # 更换实际的width
                print("raw_name = ", raw_name)
                width = new_width_real
        else:
            frame_out = transf_packed_to_raw(file_path_name, height, width, ph_height, pw_width, bw_width)
            # 替换10 bit为12 bit
            raw_name = file_path_name[:-12]
            raw_name = raw_name.replace('_10_', '_12_')
    Cb = frame_out[:, 0:width: 2]
    Cr = frame_out[:, 1:width: 2]
    # 扩展到(height，width)
    Cb = Cb.repeat(2, 0)
    Cr = Cr.repeat(2, 0)
    Cb = Cb.repeat(2, 1)
    Cr = Cr.repeat(2, 1)
    return Cb, Cr, raw_name, width


def do_ycbcr(frame_y, frame_cb, frame_cr, height, width, yuv_name):
    img_yuv = np.zeros(shape=(height, width, 3))
    img_yuv[:, :, 0] = frame_y[:, :]
    img_yuv[:, :, 1] = frame_cb[:, :]
    img_yuv[:, :, 2] = frame_cr[:, :]
    # 输出yuv
    # 创建NV21格式的yuv
    yuv_height = int(height * 1.5)
    yuv_nv21 = np.zeros(shape=(yuv_height, width))
    """
    存储方式为,前height行存Y,后height/2行存储UV
    Y Y Y Y
    Y Y Y Y
    Y Y Y Y
    U V U V
    U V U V
    """
    yuv_nv21[0:height, :] = frame_y[:, :]
    yuv_nv21[height:yuv_height, 0: width: 2] = frame_cr[0: height: 2, 0: width: 2]
    yuv_nv21[height:yuv_height, 1: width: 2] = frame_cb[0: height: 2, 0: width: 2]
    
    # 写入YUV文件
    yuv_nv21 = yuv_nv21 / 16
    yuv_nv21 = yuv_nv21.astype('uint8')
    yuv_name = yuv_name.replace('_12_', '_8_')
    yuv_nv21.tofile(yuv_name + ".nv21")
    # 转换到0~255 8bit
    img_yuv = img_yuv / 16.0
    rgb_img = np.zeros(shape=(height, width, 3))
    # YUV 转 RGB
    rgb_img[:, :, 0] = cv.add(img_yuv[:, :, 0], 1.402 * (img_yuv[:, :, 2] - 128))  # R=Y+1.402*(Cr-128)
    # G = Y -0.344136*(Cr-128)-0.714136*(Cb-128)
    rgb_img[:, :, 1] = cv.add(img_yuv[:, :, 0], - 0.34413 * (img_yuv[:, :, 1] - 128), -0.71414 * (img_yuv[:, :, 2] - 128))
    rgb_img[:, :, 2] = cv.add(img_yuv[:, :, 0], 1.772 * (img_yuv[:, :, 1] - 128))  # B=Y+1.772*(Cb - 128)
    # 换算到0~255
    rgb_img = np.clip(rgb_img, 0, 255)
    return rgb_img


def read_packed_word_12(file_path_name, height, width, ph_height, pw_width, bw_width):
    if ph_height != -1 and pw_width != -1 and bw_width != -1:
        image_bytes = bw_width * ph_height
        frame_12 = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
        print("b shape", frame_12.shape)
        print('%#x' % frame_12[0])
        frame_12.shape = [ph_height, bw_width]  # 高字节整理图像矩阵
        # 5字节读取数据
        one_byte = frame_12[:, 0:bw_width:3]
        two_byte = frame_12[:, 1:bw_width:3]
        three_byte = frame_12[:, 2:bw_width:3]
        # 数据转换防止溢出
        one_byte = one_byte.astype('uint16')
        two_byte = two_byte.astype('uint16')
        three_byte = three_byte.astype('uint16')
        # 用矩阵的方法进行像素的拼接
        one_byte = np.left_shift(np.bitwise_and(two_byte, 15), 8) + one_byte
        two_byte = np.right_shift(np.bitwise_and(two_byte, 240), 4) + np.left_shift(three_byte, 4)
        # 整合各通道数据到一起
        frame_pixels = np.zeros(shape=(ph_height, pw_width))
        frame_pixels[:, 0:pw_width:2] = one_byte[:, :]
        frame_pixels[:, 1:pw_width:2] = two_byte[:, :]
        return frame_pixels[0:height, 0:width]  # 裁剪无用数据
    else:
        new_height_12 = int(math.floor((height + 63) / 64)) * 64
        new_width_12 = int(width / 2 * 3)
        image_bytes = new_height_12 * new_width_12
        # 获取文件大小
        file_num = os.path.getsize(file_path_name)
        print("file_num: ", file_num)
        if file_num != image_bytes:
            return False
        frame_12 = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
        print("b shape", frame_12.shape)
        print('%#x' % frame_12[0])
        frame_12.shape = [new_height_12, new_width_12]  # 高字节整理图像矩阵
        # 5字节读取数据
        one_byte = frame_12[:, 0:new_width_12:3]
        two_byte = frame_12[:, 1:new_width_12:3]
        three_byte = frame_12[:, 2:new_width_12:3]
        # 数据转换防止溢出
        one_byte = one_byte.astype('uint16')
        two_byte = two_byte.astype('uint16')
        three_byte = three_byte.astype('uint16')
        # 用矩阵的方法进行像素的拼接
        one_byte = np.left_shift(np.bitwise_and(two_byte, 15), 8) + one_byte
        two_byte = np.right_shift(np.bitwise_and(two_byte, 240), 4) + np.left_shift(three_byte, 4)
        # 整合各通道数据到一起
        frame_pixels = np.zeros(shape=(new_height_12, width))
        frame_pixels[:, 0:width:2] = one_byte[:, :]
        frame_pixels[:, 1:width:2] = two_byte[:, :]

        return frame_pixels[0:height, :]

def transf_packed_to_raw(file_path_name, height, width, ph_height, pw_width, bw_width):
    print("exist PW PH and BW")
    packet_num_L, Align_num = divmod(bw_width, 5)
    image_bytes = bw_width * ph_height  # 获取图片真实的大小
    frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
    print("b shape", frame.shape)
    print('%#x' % frame[0])
    frame.shape = [ph_height, bw_width]  # 高字节整理图像矩阵
    # 5字节读取数据
    one_byte = frame[:, 0:image_bytes:5]
    two_byte = frame[:, 1:image_bytes:5]
    three_byte = frame[:, 2:image_bytes:5]
    four_byte = frame[:, 3:image_bytes:5]
    five_byte = frame[:, 4:image_bytes:5]
    # 计算补偿的0值
    if Align_num == 1:
        two_byte = np.column_stack((two_byte, np.arange(1, ph_height + 1)))
        three_byte = np.column_stack((three_byte, np.arange(1, ph_height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 1')
    elif Align_num == 2:
        three_byte = np.column_stack((three_byte, np.arange(1, ph_height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 2')
    elif Align_num == 3:
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 3')
    elif Align_num == 4:
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
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
    one_byte = np.left_shift(np.bitwise_and(two_byte, 3), 10) + np.left_shift(one_byte, 2)
    two_byte = np.bitwise_and(two_byte, 252) + np.left_shift(np.bitwise_and(three_byte, 15), 8)
    three_byte = np.right_shift(np.bitwise_and(three_byte, 240), 2) + np.left_shift(np.bitwise_and(four_byte, 63),
                                                                                    6)
    four_byte = np.right_shift(np.bitwise_and(four_byte, 192), 4) + np.left_shift(five_byte, 4)
    # 整合各通道数据到一起
    frame_pixels = np.zeros(shape=(ph_height, pw_width))
    frame_pixels[:, 0:pw_width:4] = one_byte[:, 0:packet_num_L]
    frame_pixels[:, 1:pw_width:4] = two_byte[:, 0:packet_num_L]
    frame_pixels[:, 2:pw_width:4] = three_byte[:, 0:packet_num_L]
    frame_pixels[:, 3:pw_width:4] = four_byte[:, 0:packet_num_L]
    # 裁剪无用的数据
    frame_out = frame_pixels[0:height, 0:width]
    return frame_out


def read_packed_word_cplane_12(file_path_name, height, width, ph_height, pw_width, bw_width):
    print("exist PW PH and BW")
    packet_num_L =(width + 3 )// 4
    width_byte_num = packet_num_L * 5  # 当行byte长度
    packet_num_L, Align_num = divmod(bw_width, 5)
    image_bytes = bw_width * ph_height  # 获取图片真实的大小
    frame = np.fromfile(file_path_name, count=image_bytes, dtype="uint8")
    print("b shape", frame.shape)
    print('%#x' % frame[0])
    frame.shape = [ph_height, bw_width]  # 高字节整理图像矩阵
    # 5字节读取数据
    one_byte = frame[:, 0:image_bytes:5]
    two_byte = frame[:, 1:image_bytes:5]
    three_byte = frame[:, 2:image_bytes:5]
    four_byte = frame[:, 3:image_bytes:5]
    five_byte = frame[:, 4:image_bytes:5]
    # 计算补偿的0值
    if Align_num == 1:
        two_byte = np.column_stack((two_byte, np.arange(1, ph_height + 1)))
        three_byte = np.column_stack((three_byte, np.arange(1, ph_height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 1')
    elif Align_num == 2:
        three_byte = np.column_stack((three_byte, np.arange(1, ph_height + 1)))
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 2')
    elif Align_num == 3:
        four_byte = np.column_stack((four_byte, np.arange(1, ph_height + 1)))
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
        print('Aligh is 3')
    elif Align_num == 4:
        five_byte = np.column_stack((five_byte, np.arange(1, ph_height + 1)))
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
    one_byte = np.left_shift(np.bitwise_and(two_byte, 3), 10) + np.left_shift(one_byte, 2)
    two_byte = np.bitwise_and(two_byte, 252) + np.left_shift(np.bitwise_and(three_byte, 15), 8)
    three_byte = np.right_shift(np.bitwise_and(three_byte, 240), 2) + np.left_shift(np.bitwise_and(four_byte, 63),
                                                                                    6)
    four_byte = np.right_shift(np.bitwise_and(four_byte, 192), 4) + np.left_shift(five_byte, 4)
    # 整合各通道数据到一起
    packet_num_L, Align_num = divmod(width_byte_num, 5)
    frame_pixels = np.zeros(shape=(ph_height, width))
    frame_pixels[:, 0:width:4] = one_byte[:, 0:packet_num_L]
    frame_pixels[:, 1:width:4] = two_byte[:, 0:packet_num_L]
    frame_pixels[:, 2:width:4] = three_byte[:, 0:packet_num_L]
    frame_pixels[:, 3:width:4] = four_byte[:, 0:packet_num_L]
    # 裁剪无用的数据
    frame_out = frame_pixels[0:height, 0:width]
    return frame_out


"""
def test_case_read_packed_word():

    file_name = "101907391-0060-0060-main-P1-IMGO-PW4672-PH2612-BW5840__4640x2612_10_2.packed_word"
    image, raw_name, width = read_packed_word(file_name, 2612, 4640, 2)
    image = image / 4095.0
    plt.figure(num='test', figsize=(4640, 2612))
    plt.imshow(image, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')



if __name__ == "__main__":
    print('This is main of module')
    test_case_read_packed_word()
"""