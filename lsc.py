import numpy as np
import math, os, sys
from matplotlib import pyplot as plt
import cv2

def apply_shading_to_image(img, block_size, shading_R, shading_GR, shading_GB, shading_B, pattern):
    R, GR, GB, B = raw_image.bayer_channel_separation(img, pattern)
    HH, HW = R.shape
    # 需要注意如果size不是整除的需要调整
    size_new = (HW + block_size, HH + block_size)
    # 插值
    ex_R_gain_map = cv2.resize(shading_R, size_new)
    ex_GR_gain_map = cv2.resize(shading_GR, size_new)
    ex_GB_gain_map = cv2.resize(shading_GB, size_new)
    ex_B_gain_map = cv2.resize(shading_B, size_new)
    half_b_size = int(block_size / 2)
    # 裁剪到原图大小
    R_gain_map = ex_R_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GR_gain_map = ex_GR_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GB_gain_map = ex_GB_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    B_gain_map = ex_B_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    R_new = R * R_gain_map
    GR_new = GR * GR_gain_map
    GB_new = GB * GB_gain_map
    B_new = B * B_gain_map
    new_image = raw_image.bayer_channel_integration(R_new, GR_new, GB_new, B_new, pattern)
    
    new_image = np.clip(new_image, a_min = 0, a_max = 1023)
    return new_image


def apply_shading_to_image_ratio(img, block_size, shading_R, shading_GR, shading_GB, shading_B, pattern, ratio):
    # 用G做luma
    luma_shading = (shading_GR + shading_GB) / 2
    # 计算color_shading
    R_color_shading = shading_R / luma_shading
    GR_color_shading = shading_GR / luma_shading
    GB_color_shading = shading_GB / luma_shading
    B_color_shading = shading_B / luma_shading
    # 计算调整之后luma_shading
    new_luma_shading = (luma_shading -1) * ratio + 1
    # 合并两种shading
    new_shading_R = R_color_shading * new_luma_shading
    new_shading_GR = GR_color_shading * new_luma_shading
    new_shading_GB = GB_color_shading * new_luma_shading
    new_shading_B = B_color_shading * new_luma_shading

    R, GR, GB, B = raw_image.bayer_channel_separation(img, pattern)
    HH, HW = R.shape
    size_new = (HW + block_size, HH + block_size)
    # 插值方法的选择
    ex_R_gain_map = cv2.resize(shading_R, size_new, interpolation = cv2.Inter_CUBIC)
    ex_GR_gain_map = cv2.resize(shading_GR, size_new, interpolation = cv2.Inter_CUBIC)
    ex_GB_gain_map = cv2.resize(shading_GB, size_new, interpolation = cv2.Inter_CUBIC)
    ex_B_gain_map = cv2.resize(shading_B, size_new, interpolation = cv2.Inter_CUBIC)
    
    half_b_size = int(block_size / 2)
    R_gain_map = ex_R_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GR_gain_map = ex_GR_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    GB_gain_map = ex_GB_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    B_gain_map = ex_B_gain_map[half_b_size:half_b_size + HH, half_b_size:half_b_size + HW]
    
    R_new = R * R_gain_map
    GR_new = GR * GR_gain_map
    GB_new = GB * GB_gain_map
    B_new = B * B_gain_map
    
    new_image = raw_image.bayer_channel_integration(R_new, GR_new, GB_new, B_new, pattern)
    new_image = np.clip(new_image, a_min = 0, a_max = 1023)
    return new_image


def create_lsc_data(img, block_size, pattern):
    R, GR, GB, B = raw_image.bayer_channel_separation(img, pattern)
    HH, HW = R.shape
    Hblocks = int(HH / block_size)
    Wblocks = int(HW / block_size)
    R_LSC_data = np.zeros((Hblocks, Wblocks))
    B_LSC_data = np.zeros((Hblocks, Wblocks))
    GR_LSC_data = np.zeros((Hblocks, Wblocks))
    GB_LSC_data = np.zeros((Hblocks, Wblocks))
    RA = np.zeros((Hblocks, Wblocks))
    
    center_y = HH / 2
    center_x = HW / 2
    for y in range(0, HH, block_size):
        for x in range(0, HW, block_size):
            xx = x + block_size / 2
            yy = y + block_size / 2
            block_y_num = int(y / block_size)
            block_x_num = int(x / block_size)
            RA[block_y_num, block_x_num] = (yy - center_y) * (yy - center_y) + (xx - center_x) * (xx - center_x)
            R_LSC_data[block_y_num,block_x_num] = R[y:y + block_size, x:x + block_size].mean()
            GR_LSC_data[block_y_num,block_x_num] = GR[y:y + block_size, x:x + block_size].mean()
            GB_LSC_data[block_y_num,block_x_num] = GB[y:y + block_size, x:x + block_size].mean()
            B_LSC_data[block_y_num,block_x_num] = B[y:y + block_size, x:x + block_size].mean()
    
    
    center_point = np.where(GR_LSC_data == np.max(GR_LSC_data))
    center_y = center_point[0] * block_size + block_size / 2
    center_x = center_point[1] * block_size + block_size / 2
    for y in range(0, HH, block_size):
        for x in range(0, HW, block_size):
            xx = x + block_size / 2
            yy = y + block_size / 2
            block_y_num = int(y / block_size)
            block_x_num = int(x / block_size)
            RA[block_y_num, block_x_num] = (yy - center_y) * (yy - center_y) + (xx - center_x) * (xx - center_x)
    
    RA_flatten = RA.flatten()
    R_LSC_data_flatten = R_LSC_data.flatten()
    GR_LSC_data_flatten = GR_LSC_data.flatten()
    GB_LSC_data_flatten = GB_LSC_data.flatten()
    B_LSC_data_flatten = B_LSC_data.flatten()
    
    Max_R = np.max(R_LSC_data_flatten)
    Max_GR = np.max(GR_LSC_data_flatten)
    Max_GB = np.max(GB_LSC_data_flatten)
    Max_B = np.max(B_LSC_data_flatten)
    
    G_R_LSC_data = Max_R / R_LSC_data
    G_GR_LSC_data = Max_GR / GR_LSC_data
    G_GB_LSC_data = Max_GB / GB_LSC_data
    G_B_LSC_data = Max_B / B_LSC_data
    
    R_R = R_LSC_data_flatten / np.max(R_LSC_data_flatten)
    R_GR = GR_LSC_data_flatten / np.max(GR_LSC_data_flatten)
    R_GB = GB_LSC_data_flatten / np.max(GB_LSC_data_flatten)
    R_B = B_LSC_data_flatten / np.max(B_LSC_data_flatten)
    
    plt.scatter(RA_flatten, R_B, color='blue')
    plt.scatter(RA_flatten, R_GR, color='green')
    plt.scatter(RA_flatten, R_GB, color='green')
    plt.scatter(RA_flatten, R_R, color='red')
    plt.show()
    G_R = 1 / R_R
    G_GR = 1 / R_GR
    G_GB = 1 / R_GB
    G_B = 1 / R_B
    plt.scatter(RA_flatten, G_B, color='blue')
    plt.scatter(RA_flatten, G_GR, color='green')
    plt.scatter(RA_flatten, G_GB, color='green')
    plt.scatter(RA_flatten, G_R, color='red')
    plt.show()
    
    # 重要的拟合
    par_R = np.polyfit(RA_flatten, G_R, 3)
    par_GR = np.polyfit(RA_flatten, G_GR, 3)
    par_GB = np.polyfit(RA_flatten, G_GB, 3)
    par_B = np.polyfit(RA_flatten, G_B, 3)
    
    ES_R = par_R[0] * (RA_flatten ** 3) + par_R[1] * (RA_flatten ** 2) + par_R[2] * (RA_flatten) + par_R[3]
    ES_GR = par_GR[0] * (RA_flatten ** 3) + par_GR[1] * (RA_flatten ** 2) + par_GR[2] * (RA_flatten) + par_GR[3]
    ES_GB = par_GB[0] * (RA_flatten ** 3) + par_GB[1] * (RA_flatten ** 2) + par_GB[2] * (RA_flatten) + par_GB[3]
    ES_B = par_B[0] * (RA_flatten ** 3) + par_B[1] * (RA_flatten ** 2) + par_B[2] * (RA_flatten) + par_B[3]
    plt.scatter(RA_flatten, ES_B, color='blue')
    plt.scatter(RA_flatten, ES_GR, color='green')
    plt.scatter(RA_flatten, ES_GB, color='green')
    plt.scatter(RA_flatten, ES_R, color='red')
    plt.show()
    # 通过拟合的函数
    EX_RA = np.zeros((Hblocks + 2, Wblocks + 2))
    EX_R = np.zeros((Hblocks + 2, Wblocks + 2))
    EX_GR = np.zeros((Hblocks + 2, Wblocks + 2))
    EX_GB = np.zeros((Hblocks + 2, Wblocks + 2))
    EX_B = np.zeros((Hblocks + 2, Wblocks + 2))
    new_center_y = cneter_point[0] + 1
    new_center_x = cneter_point[1] + 1 
    for y in range(0, Hblocks + 2):
        for x in range(0, Wblocks + 2):
            EX_RA[y, x] = (y- new_center_y) * block_size * (y - new_center_y) * block_size + (x- new_center_x) * block_size * (x - new_center_x) * block_size
            EX_R[y, x] = par_R[0] * (EX_RA[y, x] ** 3) + par_R[1] * (EX_RA[y, x] ** 2) + par_R[2] * (EX_RA[y, x]) + par_R[3]
            Ex_GR[y, x] = par_GR[0] * (EX_RA[y, x] ** 3) + par_GR[1] * (EX_RA[y, x] ** 2) + par_GR[2] * (EX_RA[y, x]) + par_GR[3]
            Ex_GB[y, x] = par_GB[0] * (EX_RA[y, x] ** 3) + par_GB[1] * (EX_RA[y, x] ** 2) + par_GB[2] * (EX_RA[y, x]) + par_GB[3]
            Ex_B[y, x] = par_B[0] * (EX_RA[y, x] ** 3) + par_B[1] * (EX_RA[y, x] ** 2) + par_B[2] * (EX_RA[y, x]) + par_B[3]
    
    EX_R[1:1 + Hblocks, 1:1 + Wblocks] = G_R_LSC_data
    EX_GR[1:1 + Hblocks, 1:1 + Wblocks] = G_B_LSC_data
    EX_GB[1:1 + Hblocks, 1:1 + Wblocks] = G_GB_LSC_data
    EX_B[1:1 + Hblocks, 1:1 + Wblocks] = G_B_LSC_data
    
    reture EX_R, EX_GR, EX_GB, EX_B
    
    
    
if __name__ = "__main__":
    img = 输入
    block_size = 16
    pattern = "GRBG"
    shading_R, shading_GR, shading_GB, shading_B = create_lsc_data(img, block_size, pattern)
    img2 = 输入
    new_image = apply_shading_to_image_ratio(img = img2, block_size = block_size, shading_R = shading_R, shading_GR = shading_GR, shading_GB = shading_GB, shading_B = shading_B, ratio = 1) 