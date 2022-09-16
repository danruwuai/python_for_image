#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import os
import cv2 as cv
# from matplotlib import pyplot as plt

# 读取aao数据列表
def get_aao_file(dir_path):
    file_list_aao = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list_aao.extend(os.path.join("", file) for file in files if file.endswith("aao"))
        file_list_aao.extend(os.path.join("", file) for file in files if (file.endswith("raw") and "aao_" in file))

    return file_list_aao


def load_aao():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_aao_list = get_aao_file(current_working_dir)
    # print(file_raw_list)
    # aao文件默认大小是128*128
    aao_width = 128  
    aao_height = 128
    # aao只使用了128*96存储数据
    current_height = 96
    aao_bytes = aao_height * aao_width * 32
    # 循环查找的文件
    for file_aao in file_aao_list:
        print("获取的文件：", file_aao)
        # 获取aao文件名称
        file_name = file_aao[0:file_aao.find('.')]
        frame = np.fromfile(file_aao, count=aao_bytes, dtype="uint8")
        do_aao(frame, aao_height, aao_width, current_height, file_name)

# 处理aao数据
def do_aao(frame_data, height, width, current_height, name):
    # aao实际每行的数据数
    aao_width = width * 32
    frame_data.shape = [height, aao_width]
    # 截取aao有效数据统计，即128*96
    aao_data = frame_data[0:current_height, :]
    # aao数据中，每一块的统计数据分析
    # 0，1统计R通道，4，5统计G通道，8，9统计B通道
    R_byte_low = aao_data[:, 0:aao_width:32]
    R_byte_high = aao_data[:, 1:aao_width:32]
    G_byte_low = aao_data[:, 4:aao_width:32]
    G_byte_high = aao_data[:, 5:aao_width:32]
    B_byte_low = aao_data[:, 8:aao_width:32]
    B_byte_high = aao_data[:, 9:aao_width:32]
    # 移位运算前先把数据扩充，防止溢出
    R_byte_low = R_byte_low.astype('uint16')
    R_byte_high = R_byte_high.astype('uint16')
    G_byte_low = G_byte_low.astype('uint16')
    G_byte_high = G_byte_high.astype('uint16')
    B_byte_low = B_byte_low.astype('uint16')
    B_byte_high = B_byte_high.astype('uint16')
    # 高低位运算
    R_byte = np.left_shift(R_byte_high, 8) + R_byte_low
    G_byte = np.left_shift(G_byte_high, 8) + G_byte_low
    B_byte = np.left_shift(B_byte_high, 8) + B_byte_low
    # 赋值给到输出数据
    frame_pixels = np.zeros(shape=(current_height, width,3))
    frame_pixels[:, :, 0] = R_byte
    frame_pixels[:, :, 1] = G_byte
    frame_pixels[:, :, 2] = B_byte
    # 创建CSV表格数据，内容赋值空（nan）
    csv_data = np.full([592, 128], np.NaN)
    np.savetxt(name + '1.csv', csv_data, delimiter = ",")
    csv_data = csv_data.astype('str')
    csv_data[0, 0] = "R_AVG"
    R_AVG_data = R_byte
    R_AVG_data = R_AVG_data.astype('str')
    csv_data[1: current_height + 1, 0: width] = R_AVG_data
    csv_data[99, 0] = "G_AVG"
    G_AVG_data = G_byte
    G_AVG_data = G_AVG_data.astype('str')
    csv_data[100: current_height + 100, 0: width] = G_AVG_data
    csv_data[199, 0] = "B_AVG"
    B_AVG_data = B_byte
    B_AVG_data = B_AVG_data.astype('str')
    csv_data[200: current_height + 200, 0: width] = B_AVG_data
    """
    # 显示函数直接显示效果
    frame_pixels = frame_pixels / 4095.0
    x = width / 10
    y = current_height / 10
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(frame_pixels, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')
    """
    # 输出结果到bmp，需要放置在255空间内
    frame_pixels = frame_pixels / 16.0
    # cv.imwrite(f'{raw_name}bmp', frame_raw)
    # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
    frame_pixels = frame_pixels.astype(np.float32)
    cv.imwrite(name + '.bmp', cv.cvtColor(frame_pixels, cv.COLOR_RGBA2BGRA),[int(cv.IMWRITE_JPEG_QUALITY), 100])
    
    """
    # aao数据中，每一块的统计数据分析。18位数据统计
    # 12，13，14统计R通道，16，17，18统计G通道，20，21，22统计B通道
    R_byte_low = aao_data[:, 12:aao_width:32]
    R_byte_mid = aao_data[:, 13:aao_width:32]
    R_byte_high = aao_data[:, 14:aao_width:32]
    G_byte_low = aao_data[:, 16:aao_width:32]
    G_byte_mid = aao_data[:, 17:aao_width:32]
    G_byte_high = aao_data[:, 18:aao_width:32]
    B_byte_low = aao_data[:, 20:aao_width:32]
    B_byte_mid = aao_data[:, 21:aao_width:32]
    B_byte_high = aao_data[:, 22:aao_width:32]
    
    R_byte_low = R_byte_low.astype('uint32')
    R_byte_mid = R_byte_mid.astype('uint32')
    R_byte_high = R_byte_high.astype('uint32')
    G_byte_low = G_byte_low.astype('uint32')
    G_byte_mid = G_byte_mid.astype('uint32')
    G_byte_high = G_byte_high.astype('uint32')
    B_byte_low = B_byte_low.astype('uint32')
    B_byte_mid = B_byte_mid.astype('uint32')
    B_byte_high = B_byte_high.astype('uint32')
    
    R_byte = np.left_shift(R_byte_high, 16) + np.left_shift(R_byte_mid, 8) + R_byte_low
    G_byte = np.left_shift(G_byte_high, 16) + np.left_shift(G_byte_mid, 8) + G_byte_low
    B_byte = np.left_shift(B_byte_high, 16) + np.left_shift(B_byte_mid, 8) + B_byte_low
    
    frame_pixels = np.zeros(shape=(current_height, width,3))
    frame_pixels[:, :, 0] = R_byte
    frame_pixels[:, :, 1] = G_byte
    frame_pixels[:, :, 2] = B_byte
    
    frame_pixels = frame_pixels / 262143.0
    x = width / 10
    y = current_height / 10
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(frame_pixels, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')
    
    frame_pixels = frame_pixels / 1024
    # cv.imwrite(f'{raw_name}bmp', frame_raw)
    # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
    frame_pixels = frame_pixels.astype(np.float32)
    cv.imwrite(name + '_high.bmp', cv.cvtColor(frame_pixels, cv.COLOR_RGBA2BGRA),[int(cv.IMWRITE_JPEG_QUALITY), 100])
    """
    #np.savetxt(name + '.csv', csv_data, delimiter = ",",fmt = '%.0f')
    np.savetxt(name + '.csv', csv_data, delimiter = ",", fmt = '%s')
    
if __name__ == "__main__":
    load_aao()