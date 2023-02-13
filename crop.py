#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
# import colour
# import colour.plotting
import delta_e


np.set_printoptions(suppress=True)

# region 辅助函数
# RGB2XYZ空间的系数矩阵

M = np.array([[0.412453, 0.357580, 0.180423],
              [0.212671, 0.715160, 0.072169],
              [0.019334, 0.119193, 0.950227]])


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



def show_24_color(image_file):
    image = cv.imread(image_file)
    #cv.namedWindow('imgae',cv.WINDOW_AUTOSIZE)
    #获取坐标
    r = cv.selectROI(image_file, image, False, False)
    print(r)
    # 选取roi的宽度
    width_crop = r[2]
    # 选取roi的高度
    height_crop = r[3]
    # 每一个框的宽度
    widht_crop_step = width_crop // 6
    # 每一个框的高度
    height_crop_step = height_crop // 4
    # 选取框的比例
    fill_factor = 0.5
    print(width_crop, height_crop, widht_crop_step, height_crop_step)
    # 标记框的颜色
    color = (255, 255, 0)
    # 标记框的宽度
    thickness = 1
    pt1 = []
    pt2 = []
    cv.rectangle(image, (int(r[0]),int(r[1])), (int(r[0]+r[2]),int(r[1]+r[3])), (0,0,255), 1) 
    for i in range(24):
        pt1.append((int(r[0])+ widht_crop_step * (i % 6) + int(widht_crop_step * (0.5 - fill_factor / 2)), int(r[1]) + height_crop_step * (i // 6) + int(height_crop_step * (0.5 - fill_factor / 2))))
        pt2.append((int(r[0])+ widht_crop_step * (i % 6) + int(widht_crop_step * (0.5 + fill_factor / 2)), int(r[1]) + height_crop_step * (i // 6) + int(height_crop_step * (0.5 + fill_factor / 2))))
        # 绘制矩形
        # pt1：左上角坐标， pt2：右下角坐标
        # color：线条颜色，如 (255, 0, 255) 蓝色，BGR
        # thickness：线条宽度（int）
        cv.rectangle(image, pt1[i], pt2[i], color, thickness) 
    cv.imshow('figure_name', image)# 第一个参数是窗口名称。第二个参数是图片
    cv.waitKey(0) #等待用户的按键事件
    cv.destroyAllWindows()
    return image, pt1, pt2


def save_24_color_data(image, pt1, pt2):
    size =image.shape
    print(size)
    color_data = np.zeros(shape=(24,1,3), dtype=float)
    rgb_data = np.zeros(shape=(24,1,3), dtype=np.float32)
    for i in range(24):
        # cv获取的顺序位BGR，所以要转换为RGB
        color_data[i,0,2] = image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],0].mean()
        color_data[i,0,1] = image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],1].mean()
        color_data[i,0,0] = image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],2].mean()
        rgb_data[i,0,0] = color_data[i,0,2] / 255
        rgb_data[i,0,1] = color_data[i,0,1] / 255
        rgb_data[i,0,2] = color_data[i,0,0] / 255
    
    # 使用cv转换RGB2LAB
    lab_image = cv.cvtColor(rgb_data, cv.COLOR_BGR2LAB)
    
    print(lab_image)
    # 通过转换XYZ然后转LAB
    """
    if color_data.max() > 1:
        print(color_data/255)
    else:
        print(color_data)
        color_data = color_data * 255
    
    lab_data = RGB2Lab(color_data)
    print(lab_data)
    """
    return lab_image


# region RGB 转 Lab
# 像素值RGB转XYZ空间，pixel格式:(B,G,R)
# 返回XYZ空间下的值
def __rgb2xyz__(rgb):
    rgb = degamma_srgb(rgb, clip_range=[0, 255])
    rgb = rgb / 255.0
    h,w,c = rgb.shape
    R = rgb[:,0,0]
    G = rgb[:,0,1]
    B = rgb[:,0,2]
    planed_R = R.flatten()
    planed_G = G.flatten()
    planed_B = B.flatten()
    planed_image = np.zeros((c, h*w))
    planed_image[0, :] = planed_R
    planed_image[1, :] = planed_G
    planed_image[2, :] = planed_B

    # RGB = np.array([gamma(c) for c in rgb])
    XYZ = np.dot(M, planed_image)
    #XYZ = XYZ / 255.0
    return (XYZ[0] / 0.95047, XYZ[1] / 1.0, XYZ[2] / 1.08883), h*w
    #return (XYZ[0], XYZ[1], XYZ[2]), h * w


def __xyz2lab__(xyz, size):
    """
    XYZ空间转Lab空间
    :param xyz: 像素xyz空间下的值
    :return: 返回Lab空间下的值
    """
    F_XYZ = np.zeros(shape=(3, size))
    LAB = np.zeros(shape=(size, 1, 3))
    F_XYZ[0] = [f(x) for x in xyz[0]]
    F_XYZ[1] = [f(x) for x in xyz[1]]
    F_XYZ[2] = [f(x) for x in xyz[2]]
    L = np.zeros(size)
    for i in range(size):
        L[i] = 116 * F_XYZ[1,i] - 16 if xyz[1][i] > 0.008856 else 903.3 * xyz[1][i]
    a = 500 * (F_XYZ[0,] - F_XYZ[1,])
    b = 200 * (F_XYZ[1,] - F_XYZ[2,])

    LAB[:,0,0] = L
    LAB[:,0,1] = a
    LAB[:,0,2] = b

    return LAB


def RGB2Lab(image):
    """
    RGB空间转Lab空间
    :param pixel: RGB空间像素值,格式：[G,B,R]
    :return: 返回Lab空间下的值
    """
    xyz, size = __rgb2xyz__(image)
    Lab = __xyz2lab__(xyz, size)
    return Lab

# im_channel取值范围：[0,1]
def f(im_channel):
    return np.power(im_channel, 1 / 3) if im_channel > 0.008856 else 7.787 * im_channel + 0.137931


def degamma_srgb(data, clip_range=[0, 255]):
    # bring data in range 0 to 1
    data = np.clip(data, clip_range[0], clip_range[1])
    data = np.divide(data, clip_range[1])

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
    return np.clip(data * clip_range[1], clip_range[0], clip_range[1])


"""
def cal_delta_color(lab_data):
    size =lab_data.shape
    print(size, ideal_RGB.shape)
    delta_color = np.zeros(shape=(size[0], 6))
    chroma_color = np.zeros(shape=(size[0], 2))
    # ideal_data = RGB2Lab(ideal_RGB * 255)
    ideal_data = cv.cvtColor(ideal_RGB.astype(np.float32), cv.COLOR_RGB2LAB)
    print(ideal_data)
    # CIE 1976
    # ΔE*ab = sqr((ΔL*)∗∗2 + (Δa*)∗∗2 + (Δb∗)∗∗2)
    # ΔC*ab = sqr((Δa*)∗∗2 + (Δb∗)∗∗2)
    delta_color[:, 0] = pow((lab_data[:,0,1] - ideal_data[:,0,1]) ** 2 + (lab_data[:,0,2] - ideal_data[:,0,2]) ** 2, 1/2)
    delta_color[:, 1] = pow((lab_data[:,0,0] - ideal_data[:,0,0]) ** 2 + (lab_data[:,0,1] - ideal_data[:,0,1]) ** 2 + (lab_data[:,0,2] - ideal_data[:,0,2]) ** 2, 1/2)
    # CIE 1994
    # ΔE*94 = sqr((ΔL*)**2 + (ΔC* ⁄ Sc )**2 + (ΔH* ⁄ Sh )**2 )
    # Sc = 1 + 0.045 * C*
    # Sh = 1 + 0.015 * C*
    # C* = sqr(sqr((a1*)**2 + (b1*)**2) * sqr((a2*)**2 + (b2*)**2))
    # Cs* = sqr((as*)**2 + (bs**)2)
    # ΔH* = sqr((ΔE*ab)**2 - (ΔL*)**2 -(ΔC*)**2)
    # ΔC* = sqr((a1*)∗∗2 + (b1∗)∗∗2) - sqr((a2*)∗∗2 + (b2∗)∗∗2)
    # ΔC*94 = sqr((ΔC* ⁄ Sc )**2 + (ΔH* ⁄ Sh )**2)
    delta_color[:, 2] = pow(((pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) - pow(ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2)) / (
        1 + 0.045 * (pow(pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) * pow(ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2), 1/2)))) ** 2 + (
            pow(delta_color[:, 1] ** 2 - (lab_data[:,0,0] - ideal_data[:,0,0]) ** 2 - (pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) - pow(
                ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2)), 1/2) / (1 + 0.015 * (pow(pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) * pow(
                    ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2), 1/2)))) ** 2, 1/2)
    delta_color[:, 3] = pow(((pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) - pow(ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2)) / (
        1 + 0.045 * (pow(pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) * pow(ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2), 1/2)))) ** 2 + (
            pow(delta_color[:, 1] ** 2 - (lab_data[:,0,0] - ideal_data[:,0,0]) ** 2 - (pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) - pow(
                ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2)), 1/2) / (1 + 0.015 * (pow(pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2) * pow(
                    ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2), 1/2)))) ** 2 + (lab_data[:,0,0] - ideal_data[:,0,0]) ** 2 , 1/2)
    # CIE 2000
    
    # ΔE*00 = sqr((ΔL / (Kl * Sl))**2 + (ΔC / (Kc * Sc))**2 + (ΔH / (Kh * Sh)) **2 + Rt * (ΔC / (Kc * Sc) * (ΔH / Kh * Sh)))
    # ΔL = L2* - L1*
    # L' = (L1* + L2*) / 2
    # C' = (C1* + C2*) / 2
    # a1' = a1* + a1* / 2 * (1 - sqr(C' ** 7 / (C' ** 7 + 25 ** 7)))
    # a2' = a2* + a2* / 2 * (1 - sqr(C' ** 7 / (C' ** 7 + 25 ** 7)))
    # C'' = (C1' + C2') /2
    # ΔC' = C2' - C1'
    # C1' = sqr(a1'**2 + b1* **2)
    # C2' = sqr(a2'**2 + b2* **2)
    # h1' = atan2(b1*, a1')   mod 360°
    # h2' = atan2(b2*, a2')   mod 360°
    # 
    # Δh' = h2' - h1'             |h1' - h2'| <= 180°
    # Δh' = h2' - h1' + 360°      |h1' - h2'| > 180° , h2' <= h1' 
    # Δh' = h2' - h1' - 360°      |h1' - h2'| > 180° , h2' > h1'
    # 
    # ΔH = 2* sqr(C1' * C2') * sin(Δh'/2)
    # 
    # H'' = (h1' + h2') / 2             |h1' - h2'| <= 180° 
    # H'' = (h1' + h2' + 360°) / 2      |h1' - h2'| > 180° , h1' + h2' < 360°
    # H'' = (h1' + h2' - 360°) / 2      |h1' - h2'| > 180° , h1' + h2' >= 360°
    # 
    # T = 1-0.17*cos(H'' - 30°) + 0.24 * cos(2 * H'') + 0.32 * (3 * H'' + 6°) - 0.20 * cos(4 * H'' - 63°)
    # Sl = 1 + (0.015 * (L' - 50) ** 2) / sqr(20 + (L' - 50) ** 2)
    # Sc = 1 + 0.045 * C''
    # Sh = 1 + 0.015 * C'' * T
    # Rt = -2 * sqr(C'' ** 7 / (C'' ** 7 + 25 ** 7)) * sin(60° * exp(-((H'' - 275°)/25°)**2))
    # 
    # ΔC*00 = sqr((ΔC / (Kc * Sc))**2 + (ΔH / (Kh * Sh)) **2 + Rt * (ΔC / (Kc * Sc) * (ΔH / Kh * Sh)))
    # 
    # http://www.ece.rochester.edu/~/gsharma/ciede2000/

    
    
    chroma_color[:, 0] = pow(lab_data[:,0,1] ** 2 + lab_data[:,0,2] ** 2, 1/2)
    chroma_color[:, 1] = pow(ideal_data[:,0,1] ** 2 + ideal_data[:,0,2] ** 2, 1/2)
    mean_chroma = chroma_color[:, 0].mean() / chroma_color[:, 1].mean()* 100
    mean_delta_c = delta_color[:, 0].mean()
    mean_delta_e = delta_color[:, 1].mean()
    print(delta_color)
    print(mean_chroma)
    print(mean_delta_c)
    print(mean_delta_e)
    return delta_color, round(mean_chroma, 1), round(mean_delta_c, 2), round(mean_delta_e, 2), ideal_data
"""


def cal_delta_color(lab_data):
    ideal_data = cv.cvtColor(ideal_RGB.astype(np.float32), cv.COLOR_RGB2LAB)
    delta_color = {}
    delta_color["lab_data"] = lab_data
    delta_color["ideal_data"] = ideal_data
    delta_color["delta_c_ab"], delta_color["delta_e_ab"] = delta_e.delta_E_CIE1976(lab_data, ideal_data)
    delta_color["delta_c_94"], delta_color["delta_e_94"] = delta_e.delta_E_CIE1994(lab_data, ideal_data)
    delta_color["delta_c_00"], delta_color["delta_e_00"] = delta_e.delta_E_CIE2000(lab_data, ideal_data)
    delta_color["delta_c_ab_mean"] = round(delta_color["delta_c_ab"].mean(), 2)
    delta_color["delta_c_ab_max"] = round(delta_color["delta_c_ab"].max(), 2)
    delta_color["delta_e_ab_mean"] = round(delta_color["delta_e_ab"].mean(), 2)
    delta_color["delta_e_ab_max"] = round(delta_color["delta_e_ab"].max(), 2)
    delta_color["delta_c_94_mean"] = round(delta_color["delta_c_94"].mean(), 2)
    delta_color["delta_c_94_max"] = round(delta_color["delta_c_94"].max(), 2)
    delta_color["delta_e_94_mean"] = round(delta_color["delta_e_94"].mean(), 2)
    delta_color["delta_e_94_max"] = round(delta_color["delta_e_94"].max(), 2)
    delta_color["delta_c_00_mean"] = round(delta_color["delta_c_00"].mean(), 2)
    delta_color["delta_c_00_max"] = round(delta_color["delta_c_00"].max(), 2)
    delta_color["delta_e_00_mean"] = round(delta_color["delta_e_00"].mean(), 2)
    delta_color["delta_e_00_max"] = round(delta_color["delta_e_00"].max(), 2)
    delta_color["delta_chroma_color"] = round((np.sqrt(lab_data[0:18,0,1] ** 2 + lab_data[0:18,0,2] ** 2) / np.sqrt(ideal_data[0:18,0,1] ** 2 + ideal_data[0:18,0,2] ** 2)).mean() * 100, 2)
    print(delta_color)
    return delta_color


def color_show(image_file, delta_color):
    # 设置图片大小
    plt.figure(num=3, figsize=(8, 10))
    # 设置Camera点图
    plt.scatter(delta_color["lab_data"][:,0,1], delta_color["lab_data"][:,0,2], color=ideal_RGB, marker='o', s=100, label='Camera')  # 蓝色圆点实线    # 设置Ideal点图
    plt.scatter(delta_color["ideal_data"][:,0,1], delta_color["ideal_data"][:,0,2], color=ideal_RGB, marker='s', s=100, label='Ideal')  # 蓝色圆点实线
    # 设置图例
    plt.legend(loc='upper left')
    # 设置坐标轴范围
    plt.xlim(-70, 80)
    plt.ylim(-70, 100)
    # 设置坐标轴名称
    plt.xlabel('a*')
    plt.ylabel('b*')
    # 设置坐标轴刻度
    my_x_ticks = np.arange(-60, 80, 20)
    my_y_ticks = np.arange(-60, 100, 20)
    # 设置图片标题
    plt.title(image_file, fontsize=16)
    # 设置0刻度虚线
    plt.axvline(x=0, ymin=0, ymax=0.9, linestyle='--', color='gray')
    plt.axhline(y=0, xmin=0, xmax=1, linestyle='--', color='gray')
    # 设置色块注释
    for i in range(18): 
        plt.annotate(str(i+1), xy=(delta_color["lab_data"][i,0,1], delta_color["lab_data"][i,0,2]), xytext=(delta_color["lab_data"][i,0,1] + 3, delta_color["lab_data"][i,0,2]), fontsize=13, color=ideal_RGB[i,0])
        plt.plot((delta_color["lab_data"][i,0,1], delta_color["ideal_data"][i,0,1]), (delta_color["lab_data"][i,0,2], delta_color["ideal_data"][i,0,2]), color=ideal_RGB[i,0])
    # 设置计算结果注释
    plt.text(75, 95, 'Mean camera chroma (saturation) = ' + str(delta_color["delta_chroma_color"]) +'%', fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 90, 'ΔC ab uncorr: mean = ' + str(delta_color["delta_c_ab_mean"]) + ' ; max = ' + str(round(delta_color["delta_c_ab_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 85, 'ΔE ab: mean = ' + str(delta_color["delta_e_ab_mean"]) + ' ; max = ' + str(round(delta_color["delta_e_ab_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 80, 'ΔC 94 uncorr: mean = ' + str(delta_color["delta_c_94_mean"]) + ' ; max = ' + str(round(delta_color["delta_c_94_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 75, 'ΔE 94: mean = ' + str(delta_color["delta_e_94_mean"]) + ' ; max = ' + str(round(delta_color["delta_e_94_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 70, 'ΔC 00 uncorr: mean = ' + str(delta_color["delta_c_00_mean"]) + ' ; max = ' + str(round(delta_color["delta_c_00_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    plt.text(75, 65, 'ΔE 00: mean = ' + str(delta_color["delta_e_00_mean"]) + ' ; max = ' + str(round(delta_color["delta_e_00_max"], 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})

    # plt.text(75, 80, 'W Bal (Zones 2-5) ΔC 00 = ' + str(round(delta_color["delta_e_00"][19:23].max(), 1)), fontdict = {'fontsize': 10, 'color': 'black', 'ha': 'right'})
    #plt.annotate('Mean camera chroma (saturation) = ' + str(mean_chroma) +'%', xy=(0, 95), xytext=(0, 95), fontsize=10, color='black')
    #plt.annotate('ΔC 00 uncorr: mean = ' + str(mean_delta_c) + ' ; max = ' + str(mean_delta_c), xy=(0, 90), xytext=(0, 90), fontsize=10, color='black')
    #plt.annotate('ΔE 00: mean = ' + str(mean_delta_e) + ' ; max = ' + str(mean_delta_e), xy=(11, 85), xytext=(11, 85), fontsize=10, color='black')

    # colour.plotting.plot_chromaticity_diagram_CIE1931(standalone=False)  

    
    plt.show()





if __name__ == '__main__':
    # image_file = 'TL84_1_calibrated.jpg'
    image_file = 'TL84_1_calibrated.jpg'
    image, pt1, pt2 = show_24_color(image_file)
    lab_data = save_24_color_data(image, pt1, pt2)
    delta_color = cal_delta_color(lab_data)
    color_show(image_file, delta_color)