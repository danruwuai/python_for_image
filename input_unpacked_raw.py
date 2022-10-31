#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import cProfile
import numpy as np
import os
import cv2 as cv
import do_pure_raw
import read_unpack_raw as read_unpackraw
from matplotlib import pyplot as plt
import do_sdblk
import demosaic
from multiprocessing import Process
import do_awb,do_gtm

# import raw_image_show as show


def get_raw_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("raw") and os.path.isfile(file)))

    return file_list


def load_raw():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_raw_list = get_raw_file(current_working_dir)
    # print(file_raw_list)
    # 循环查找raw的文件
    for file_raw in file_raw_list:
        print("获取的文件：", file_raw)
        # 获取raw对应的信息
        raw_info = file_raw[file_raw.find('__'):file_raw.find('.') + 1]
        raw_height = raw_info[raw_info.find('x') + 1:raw_info.find('.') - 5]
        raw_width = raw_info[raw_info.find('__') + 2:raw_info.find('x')]
        raw_bayer = raw_info[raw_info.find('.') - 1:raw_info.find('.')]
        raw_bit = raw_info[raw_info.find('.') - 4:raw_info.find('.') - 2]
        # 字符串转int
        raw_height = int(raw_height)
        raw_width = int(raw_width)
        raw_bayer = int(raw_bayer)
        raw_bit = int(raw_bit)
        print("width:", raw_width)
        print("height:", raw_height)
        print("bayer:", raw_bayer)
        print("bit:", raw_bit)
        obj = Process(target=do_raw, args=(file_raw, raw_height, raw_width, raw_bayer, raw_bit))  # args
        # 以元组的形式给子进程func函数传位置参数
        obj.start()  # 执行子进程对象
        # do_raw(file_raw, raw_height, raw_width, raw_bayer, raw_bit)


def pure_raw_isp(image, raw_height, raw_width, raw_bit, raw_bayer, raw_name):
    if 0:
        # 输出csv数据
        do_pure_raw.raw_to_csv(image, raw_height, raw_width, raw_bayer, raw_name)
    # 输出pure_raw对应的bmp
    pure_raw_rgb_data = do_pure_raw.do_bayer_color(image, raw_height, raw_width, raw_bayer)
    save_bmp(pure_raw_rgb_data, raw_bit, raw_name + '_pure_raw')
    # OB处理
    pure_obc_data = do_pure_raw.do_black_level_correction(image, raw_bit)
    # 去马赛克处理
    # frame_cfa_rgb = demosaic.AHD(pure_obc_data, raw_bayer)
    frame_cfa_rgb = demosaic.AH_demosaic(pure_obc_data, raw_bayer)
    # frame_cfa_rgb = demosaic.blinnear(pure_obc_data, raw_bayer)
    save_bmp(frame_cfa_rgb, raw_bit, raw_name + '_pure_cfa')
    print("################################################################")
    # AWB处理
    pure_awb_data = do_awb.do_awb(frame_cfa_rgb)
    save_bmp(pure_awb_data, raw_bit, raw_name + '_pure_awb')
    print("################################################################")
    # ggm处理
    pure_gtm_data = do_gtm.do_ggm(pure_awb_data, raw_bit)
    save_bmp(pure_gtm_data, raw_bit, raw_name + '_pure_ggm')


def raw_image_show_fakecolor(image, height, width, bits):
    x = width / 100
    y = height / 100
    image = image / (2.0 ** bits - 1)
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(image, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')


# 处理raw函数
def do_raw(file_raw, raw_height, raw_width, raw_bayer, raw_bit):
    frame_data = read_unpackraw.read_unpack_file(file_raw, raw_height, raw_width, raw_bit)
    # image = frame_data / 4095.
    # show.raw_image_show_thumbnail(image, raw_height, raw_width)
    # do_pure_raw.histogram_show(frame_data, raw_bit)
    raw_name = file_raw[:file_raw.find('.')]
    # pure_raw_isp 子进程进入
    obj = Process(target=pure_raw_isp,
                  args=(frame_data, raw_height, raw_width, raw_bit, raw_bayer, raw_name))  # args以元组的形式给子进程func函数传位置参数
    # kwargs以字典的形式给子进程func函数传关键字参数
    # kwargs={'name': '小杨', 'age': 18}
    obj.start()  # 执行子进程对象
    # pure_raw处理
    frame_obc_data = do_pure_raw.do_black_level_correction(frame_data, raw_bit)
    lsc_mask = raw_name[:19]
    print("lsc_mask:", lsc_mask)
    frame_lsc_data, lsc_flag = do_sdblk.do_lsc_for_raw(frame_obc_data, raw_bayer, lsc_mask)
    if not lsc_flag:
        print("################################################################")
        print("不存在对应的sdblk,不做LSC处理")
    else:
        rgb_lsc_data = do_pure_raw.do_bayer_color(frame_lsc_data, raw_height, raw_width, raw_bayer)
        save_bmp(rgb_lsc_data, raw_bit, raw_name + '_proc_raw')
        # frame_cfa_rgb = demosaic.AHD(frame_lsc_data, raw_bayer)
        frame_cfa_rgb = demosaic.AH_demosaic(frame_lsc_data, raw_bayer)
        # frame_cfa_rgb = demosaic.blinnear(frame_lsc_data, raw_bayer)
        save_bmp(frame_cfa_rgb, raw_bit, raw_name + '_proc_cfa')
        # raw_image_show_fakecolor(rgb_data, raw_height, raw_width, raw_bit)
        print("################################################################")
        # AWB处理
        awb_data = do_awb.do_awb(frame_cfa_rgb)
        save_bmp(awb_data, raw_bit, raw_name + '_proc_awb')
        print("################################################################")
        # GGM处理
        gtm_data = do_gtm.do_ggm(awb_data, raw_bit)
        save_bmp(gtm_data, raw_bit, raw_name + '_proc_ggm')


def save_bmp(img, bit, name):
    img[img < 0] = 0
    img = img / (2**(bit - 8))
    # cv.imwrite(f'{raw_name}bmp', frame_raw)
    # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出
    img = np.clip(img, 0, 255)
    img = img.astype(np.uint8)
    cv.imwrite(f'{name}.bmp', cv.cvtColor(img, cv.COLOR_RGBA2BGRA))


if __name__ == "__main__":
    print("################################################################")
    print("Design by Zhong")
    print("Creation time:2022/09/10")
    print("################################################################")
    cProfile.run('load_raw()')
    # load_raw()
