#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
# import cProfile
import numpy as np
import os, shutil
import cv2 as cv
import do_pure_raw
import read_unpack_raw as read_unpackraw
from matplotlib import pyplot as plt
import do_sdblk
import demosaic
from multiprocessing import Process
import do_awb
import do_gtm
import read_packed_word as readpackedword
import degamma

# import raw_image_show as show

ideal_RGB = np.array([[[0.447, 0.317, 0.265]],
                      [[0.764, 0.580, 0.501]],
                      [[0.364, 0.480, 0.612]],
                      [[0.355, 0.422, 0.253]],
                      [[0.507, 0.502, 0.691]],
                      [[0.382, 0.749, 0.670]],
                      [[0.867, 0.481, 0.187]],
                      [[0.277, 0.356, 0.668]],
                      [[0.758, 0.322, 0.382]],
                      [[0.361, 0.225, 0.417]],
                      [[0.629, 0.742, 0.242]],
                      [[0.895, 0.630, 0.162]],
                      [[0.155, 0.246, 0.576]],
                      [[0.277, 0.588, 0.285]],
                      [[0.681, 0.199, 0.223]],
                      [[0.928, 0.777, 0.077]],
                      [[0.738, 0.329, 0.594]],
                      [[0.000, 0.540, 0.66]],
                      [[0.960, 0.962, 0.950]],
                      [[0.786, 0.793, 0.793]],
                      [[0.631, 0.639, 0.640]],
                      [[0.474, 0.475, 0.477]],
                      [[0.324, 0.330, 0.336]],
                      [[0.191, 0.194, 0.199]]])


def get_raw_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("raw") and os.path.isfile(file)))

    return file_list

def get_packed_word_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):  # 遍历所有子目录        
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith('.packed_word') and '-yplane-' not in file and 'cplane' not in file and os.path.isfile(file)  and not os.path.isfile(os.path.splitext(file)[0].replace('_10_', '_12_') +".raw")))
        # print(file_list)
    return file_list


def load_raw(show_lsc_flag):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_raw_list = get_raw_file(current_working_dir)
    file_packed_word_list = get_packed_word_file(current_working_dir)
    file_list = file_raw_list + file_packed_word_list
    # print(file_raw_list,file_packed_word_list)
    # print(file_list)
    if file_list:
        if os.path.exists('Result'):
            shutil.rmtree('Result')
        os.makedirs('Result')
    # 循环查找raw的文件
    for file_raw in file_list:
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
        # obj = Process(target=do_raw, args=(file_raw, raw_height, raw_width, raw_bayer, raw_bit))  # args
        # 以元组的形式给子进程func函数传位置参数
        # obj.start()  # 执行子进程对象
        do_raw(file_raw, raw_height, raw_width, raw_bayer, raw_bit, show_lsc_flag)


# 处理raw函数
def do_raw(file_raw, raw_height, raw_width, raw_bayer, raw_bit, show_lsc_flag):
    yuv_flag = 0
    if file_raw.endswith("raw"):
        frame_data = read_unpackraw.read_unpack_file(file_raw, raw_height, raw_width, raw_bit)
        raw_name = file_raw[:file_raw.find('.')]
    elif file_raw.endswith('.packed_word'):
        frame_data, raw_name, width, yuv_flag = readpackedword.read_packed_word(
            file_raw, raw_height, raw_width, raw_bit)
        # packed_word转12bit raw，需要更新bit位
        if raw_bit == 10:
            raw_bit = 12
    else:
        return False
    # image = frame_data / 4095.
    # show.raw_image_show_thumbnail(image, raw_height, raw_width)
    # do_pure_raw.histogram_show(frame_data, raw_bit)
    if yuv_flag == 1:
        save_bmp(frame_data, raw_bit, 'Result/' + raw_name + '_yuv')
        return False
    # 获取raw图前面mask信息
    jpg_mask = raw_name[:17]
    print("jpg_mask:", jpg_mask)

    # kwargs以字典的形式给子进程func函数传关键字参数
    # kwargs={'name': '小杨', 'age': 18}
    # pure_raw处理
    frame_obc_data = do_pure_raw.do_black_level_correction(frame_data, raw_bit)
    frame_lsc_data, lsc_flag = do_sdblk.do_lsc_for_raw(frame_obc_data, raw_height, raw_width, raw_bayer, jpg_mask, show_lsc_flag, raw_name)
    if not lsc_flag:
        print("################################################################")
        print("不存在对应的sdblk,不做LSC处理")
    else:
        rgb_lsc_data = do_pure_raw.do_bayer_color(frame_lsc_data, raw_height, raw_width, raw_bayer)
        save_bmp(rgb_lsc_data, raw_bit, 'Result/' + raw_name + '_proc_raw')
        # frame_cfa_rgb = demosaic.AHD(frame_lsc_data, raw_bayer)
        frame_cfa_rgb = demosaic.AH_demosaic(frame_lsc_data, raw_bayer)
        # frame_cfa_rgb = demosaic.blinnear(frame_lsc_data, raw_bayer)
        save_bmp(frame_cfa_rgb, raw_bit, 'Result/' + raw_name + '_proc_cfa')
        # raw_image_show_fakecolor(rgb_data, raw_height, raw_width, raw_bit)
        print("################################################################")
        frame_cfa_rgb[frame_cfa_rgb < 0] = 0
        img = frame_cfa_rgb / (2**(raw_bit - 8))
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出
        img = np.clip(img, 0, 255)
        img = img.astype(np.uint8)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        # # 显示
        cv.namedWindow('img', 0)  
        cv.namedWindow('img', cv.WINDOW_NORMAL)
        cv.imshow('img', img)
        cv.waitKey(3)
 
        detector = cv.mcc.CCheckerDetector_create()
 
        detector.process(img, cv.mcc.MCC24)
 
        # cv2.mcc_CCheckerDetector.getBestColorChecker()
        checker = detector.getBestColorChecker()
 
        cdraw = cv.mcc.CCheckerDraw_create(checker)
        img_draw = img.copy()
        cdraw.draw(img_draw)
        cv.namedWindow('img_draw', cv.WINDOW_NORMAL)
        cv.imshow('img_draw', img_draw)
        cv.waitKey(6)
        
        chartsRGB = checker.getChartsRGB()
 
        src = chartsRGB[:,1].copy().reshape(24, 1, 3)
        print(src)
        awb_rg = (src[19:23, 0, 0]/src[19:23, 0, 1]).mean()
        awb_bg = (src[19:23, 0, 2]/src[19:23, 0, 1]).mean()
        #awb_rg = (src[19,0,0]/src[19,0,1]+src[20,0,0]/src[20,0,1]+src[21,0,0]/src[21,0,1]+src[22,0,0]/src[22,0,1]) / 4
        #awb_bg = (src[19,0,2]/src[19,0,1]+src[20,0,2]/src[20,0,1]+src[21,0,2]/src[21,0,1]+src[22,0,2]/src[22,0,1]) / 4
        print(awb_rg, awb_bg)
        # AWB处理
        awb_data = do_awb(frame_cfa_rgb, awb_rg, awb_bg)
        save_bmp(awb_data, raw_bit, 'Result/' + raw_name + '_proc_awb')
        print("################################################################")
        awb_data[awb_data < 0] = 0
        img = awb_data / (2**(raw_bit - 8))
        # cv.imwrite(f'{raw_name}bmp', frame_raw)
        # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出
        img = np.clip(img, 0, 255)
        img = img.astype(np.uint8)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        # # 显示
        cv.namedWindow('img', 0)  
        cv.namedWindow('img', cv.WINDOW_NORMAL)
        cv.imshow('img', img)
        cv.waitKey(3)

        detector = cv.mcc.CCheckerDetector_create()

        detector.process(img, cv.mcc.MCC24)

        # cv2.mcc_CCheckerDetector.getBestColorChecker()
        checker = detector.getBestColorChecker()

        cdraw = cv.mcc.CCheckerDraw_create(checker)
        img_draw = img.copy()
        cdraw.draw(img_draw)
        cv.namedWindow('img_draw', cv.WINDOW_NORMAL)
        cv.imshow('img_draw', img_draw)
        cv.waitKey(0)

        chartsRGB = checker.getChartsRGB()

        src = chartsRGB[:,1].copy().reshape(24, 1, 3)

        src /= 255.0

        print(src.shape)
        
        
        # rgb = degamma_srgb(ideal_RGB)
        rgb = degamma.do_deggm(ideal_RGB)
        print("#############/n",src,rgb)
        # model1 = cv2.ccm_ColorCorrectionModel(src, cv2.mcc.MCC24)
        model1 = cv.ccm_ColorCorrectionModel(src, rgb, cv.ccm.COLOR_SPACE_sRGBL)
        # model1 = cv2.ccm_ColorCorrectionModel(src,src,cv2.ccm.COLOR_SPACE_sRGB)
        model1.run()
        ccm = model1.getCCM()
        print("ccm ", ccm)
        loss = model1.getLoss()
        print("loss ", loss)

        # CCM处理
        ccm_data = do_ccm(awb_data, ccm)
        save_bmp(ccm_data, raw_bit, 'Result/' + raw_name + '_proc_ccm')
        print("################################################################")
        # GGM处理
        gtm_data = do_gtm.do_ggm(ccm_data, raw_bit)
        save_bmp(gtm_data, raw_bit, 'Result/' + raw_name + '_proc_ggm')



def save_bmp(img, bit, name):
    img[img < 0] = 0
    img = img / (2**(bit - 8))
    # cv.imwrite(f'{raw_name}bmp', frame_raw)
    # imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出
    img = np.clip(img, 0, 255)
    img = img.astype(np.uint8)
    cv.imwrite(f'{name}.bmp', cv.cvtColor(img, cv.COLOR_RGBA2BGRA))


def do_awb(image, awb_rg, awb_bg):
    
    image[:, :, 0] = image[:, :, 0] / awb_rg
    # image[:, :, 1] = image[:, :, 1] / 1
    image[:, :, 2] = image[:, :, 2] / awb_bg
        
    image = image.astype(np.uint16)
    return image


def degamma_srgb(data, clip_range=[0, 255]):
    # bring data in range 0 to 1

    data = np.asarray(data)
    mask = data > 0.04045

    # basically, if data[x, y, c] > 0.04045, data[x, y, c] = ( (data[x, y, c] + 0.055) / 1.055 ) ^ 2.4
    #            else, data[x, y, c] = data[x, y, c] / 12.92
    data[mask] += 0.055
    data[mask] /= 1.055
    data[mask] **= 2.4

    data[np.invert(mask)] /= 12.92

    #data_show = data.copy()
    #np.clip(data_show * clip_range[1], clip_range[0], clip_range[1])
    # gbr = rgb[...,[2,0,1]]
    # data_show = data_show[..., ::-1]
    #data_show = data_show[..., [2,1,0]]
    #cv.imshow("data", data_show)
    #cv.waitKey(0)
    

    # rescale
    return data


def do_ccm(image, ccm):

    output = np.empty(np.shape(image), dtype=np.float32)
    output[:, :, 0] = ccm[0, 0] * image[:, :, 0] + ccm[1, 0] * image[:, :, 1] + ccm[
        2, 0] * image[:, :, 2]
    output[:, :, 1] = ccm[0, 1] * image[:, :, 0] + ccm[1, 1] * image[:, :, 1] + ccm[
        2, 1] * image[:, :, 2]
    output[:, :, 2] = ccm[0, 2] * image[:, :, 0] + ccm[1, 2] * image[:, :, 1] + ccm[
        2, 2] * image[:, :, 2]

    CCM_0 = ccm[0,0] + ccm[1,0] + ccm[2,0] 
    CCM_1 = ccm[0,1] + ccm[1,1] + ccm[2,1] 
    CCM_2 = ccm[0,2] + ccm[1,2] + ccm[2,2] 
    
    print(CCM_0, CCM_1, CCM_2)
    output[output < 0] = 0
    output = output.astype(np.uint16)
    return output

if __name__ == "__main__":
    print("################################################################")
    print("Design by Zhong")
    print("Creation time:2022/09/10")
    print("################################################################")
    # cProfile.run('load_raw()') #  查看时间
    load_raw(False)
    np.linalg.lstsq