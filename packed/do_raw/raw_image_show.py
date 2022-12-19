#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3

# import cv2 as cv
import numpy as np
# import os
from matplotlib import pyplot as plt

# from scipy import misc
# from mpl_toolkits.mplot3d import Axes3D

'''
mono, the image data value is between 0~1
'''


# 黑白全尺show
def raw_image_show_fullsize(image, height, width):
    x = width / 100
    y = height / 100
    plt.figure(num='text', figsize=(x, y))
    plt.imshow(image, cmap='gray', interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])  # 隐藏x轴和Y轴的标记位置和labels
    plt.show()
    print('show')


def raw_image_show_3D(image, height, width):
    # fig = plt.figure()
    # ax=Axes3d(fig)
    ax = plt.subplot(1, 1, 1, projection='3d')
    X = np.arange(0, width)
    Y = np.arange(0, height)
    X, Y = np.meshgrid(X, Y)
    # R = np.sqrt(X ** 2 + Y ** 2)
    Z = image
    # 具体函数方法可用help(function)查看，如：help（ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
    plt.show()
    print('show')


def raw_image_show_lsc(lsc_R, lsc_GR, lsc_GB, lsc_B, height, width, name):
    fig, ax = plt.subplots(2, 2, figsize=(10, 4.5))
    X = np.arange(0, width)
    Y = np.arange(0, height)
    X, Y = np.meshgrid(X, Y)
    ax[0][0].set_title('LSC_R', color='r', loc="left")  # 设置标题
    ax[0][0].axis('off')
    ax[0][0] = fig.add_subplot(2, 2, 1, projection='3d')
    ax[0][0].plot_wireframe(X, Y, lsc_R, rstride=100, cstride=100, color='r')
    ax[0][1].set_title('LSC_GR', color='g', loc="left")  # 设置标题
    ax[0][1].axis('off')
    ax[0][1] = fig.add_subplot(2, 2, 2, projection='3d')
    ax[0][1].plot_wireframe(X, Y, lsc_GR, rstride=100, cstride=100, color='g')
    ax[1][0].set_title('LSC_GB', color='g', loc="left")  # 设置标题
    ax[1][0].axis('off')
    ax[1][0] = fig.add_subplot(2, 2, 3, projection='3d')
    ax[1][0].plot_wireframe(X, Y, lsc_GB, rstride=100, cstride=100, color='g')
    ax[1][1].set_title('LSC_B', color='b', loc="left")  # 设置标题
    ax[1][1].axis('off')
    ax[1][1] = fig.add_subplot(2, 2, 4, projection='3d')
    ax[1][1].plot_wireframe(X, Y, lsc_B, rstride=100, cstride=100, color='b')
    plt.savefig('Result/' + name + '.jpg', bbox_inches='tight', dpi=300)
    # plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    # 全屏显示
    plt.suptitle(name)
    manager = plt.get_current_fig_manager()
    try:
        manager.window.showMaximized()
        print("show_MAX_screen")
    except AttributeError:
        # manager.full_screen_toggle()
        pass
        print("no MAX_screen")
    # manager.window.showMaximized()

    plt.ion()
    plt.pause(30)
    # plt.show()
    plt.close()

    # ax=Axes3d(fig)
    """
    ax = plt.subplot(2, 2, 1, projection='3d')
    ax.set_title('LSC_R')  # 设置标题
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)
    X = np.arange(0, width)
    Y = np.arange(0, height)
    X, Y = np.meshgrid(X, Y)
    # R = np.sqrt(X ** 2 + Y ** 2)
    # 具体函数方法可用help(function)查看，如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_R, rstride=10, cstride=10, color='r')
    ax = plt.subplot(2, 2, 2, projection='3d')
    ax.set_title('LSC_GR')  # 设置标题
    # 具体函数方法可用help(function)查看,如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_GR, rstride=10, cstride=10, color='g')
    ax = plt.subplot(2, 2, 3, projection='3d')
    ax.set_title('LSC_GB', y=-0.3)  # 设置标题
    # 具体函数方法可用help(function)查看，如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_GB, rstride=10, cstride=10, color='g')
    ax = plt.subplot(2, 2, 4, projection='3d')
    ax.set_title('LSC_B', y=-0.3)  # 设置标题
    # 具体函数方法可用help(function)查看,如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_B, rstride=10, cstride=10, color='b')
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    plt.show()
    """
    print('show')


def raw_image_show_raw(R, GR, GB, B, height, width, name):
    fig, ax = plt.subplots(2, 2, figsize=(10, 4.5))
    X = np.arange(0, width)
    Y = np.arange(0, height)
    X, Y = np.meshgrid(X, Y)
    ax[0][0].set_title('R', color='r', loc="left")  # 设置标题
    ax[0][0].axis('off')
    ax[0][0] = fig.add_subplot(2, 2, 1, projection='3d')
    ax[0][0].plot_wireframe(X, Y, R, rstride=width // 8, cstride=height // 8, color='r')
    ax[0][0].set_zlim(R.min(), R.max())
    ax[0][1].set_title('GR', color='g', loc="left")  # 设置标题
    ax[0][1].axis('off')
    ax[0][1] = fig.add_subplot(2, 2, 2, projection='3d')
    ax[0][1].plot_wireframe(X, Y, GR, rstride=width // 8, cstride=height // 8, color='g')
    ax[0][1].set_zlim(GR.min(), GR.max())
    ax[1][0].set_title('GB', color='g', loc="left")  # 设置标题
    ax[1][0].axis('off')
    ax[1][0] = fig.add_subplot(2, 2, 3, projection='3d')
    ax[1][0].plot_wireframe(X, Y, GB, rstride=width // 8, cstride=height // 8, color='g')
    ax[1][0].set_zlim(GB.min(), GB.max())
    ax[1][1].set_title('B', color='b', loc="left")  # 设置标题
    ax[1][1].axis('off')
    ax[1][1] = fig.add_subplot(2, 2, 4, projection='3d')
    ax[1][1].plot_wireframe(X, Y, B, rstride=width // 8, cstride=height // 8, color='b')
    ax[1][1].set_zlim(B.min(), B.max())
    # plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    plt.savefig('Result/' + name+'.jpg', bbox_inches='tight', dpi=300)
    # 全屏显示
    plt.suptitle(name)
    manager = plt.get_current_fig_manager()
    try:
        # manager.window.showMaximized()
        manager.resize(*manager.window.maxsize())
        print("show_MAX_screen")
    except AttributeError:
        # manager.full_screen_toggle()
        pass
        print("no MAX Screen")
    # manager.window.showMaximized()

    plt.ion()
    plt.pause(60)
    # plt.show()
    plt.close()

    # ax=Axes3d(fig)
    """
    ax = plt.subplot(2, 2, 1, projection='3d')
    ax.set_title('LSC_R')  # 设置标题
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)
    X = np.arange(0, width)
    Y = np.arange(0, height)
    X, Y = np.meshgrid(X, Y)
    # R = np.sqrt(X ** 2 + Y ** 2)
    # 具体函数方法可用help(function)查看，如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_R, rstride=10, cstride=10, color='r')
    ax = plt.subplot(2, 2, 2, projection='3d')
    ax.set_title('LSC_GR')  # 设置标题
    # 具体函数方法可用help(function)查看,如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_GR, rstride=10, cstride=10, color='g')
    ax = plt.subplot(2, 2, 3, projection='3d')
    ax.set_title('LSC_GB', y=-0.3)  # 设置标题
    # 具体函数方法可用help(function)查看，如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_GB, rstride=10, cstride=10, color='g')
    ax = plt.subplot(2, 2, 4, projection='3d')
    ax.set_title('LSC_B', y=-0.3)  # 设置标题
    # 具体函数方法可用help(function)查看,如:help(ax.plot_surface)
    # ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    ax.plot_wireframe(X, Y, lsc_B, rstride=10, cstride=10, color='b')
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    plt.show()
    """
    print('show')


# 黑白小尺寸show
def raw_image_show_thumbnail(image, height, width):
    x = width / 800
    y = height / 800
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(image, cmap='gray', interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()


def raw_image_show_fakecolor(image, height, width, pattern):
    x = width / 100
    y = height / 100
    rgb_img = np.zeros(shape=(height, width, 3))
    R = rgb_img[:, :, 0]
    GR = rgb_img[:, :, 1]
    GB = rgb_img[:, :, 1]
    B = rgb_img[:, :, 2]
    # 0:B 1:GB 2:GR 3:R
    if pattern == "RGGB":
        R[::2, ::2] = image[::2, ::2]
        GR[::2, 1::2] = image[::2, 1::2]
        GB[1::2, ::2] = image[1::2, ::2]
        B[1::2, 1::2] = image[1::2, 1::2]
    elif pattern == " GRBG":
        GR[::2, ::2] = image[::2, ::2]
        R[::2, 1::2] = image[::2, 1::2]
        B[1::2, ::2] = image[1::2, ::2]
        GB[1::2, 1::2] = image[1::2, 1::2]
    elif pattern == "GBRG":
        GB[::2, ::2] = image[::2, ::2]
        B[::2, 1::2] = image[::2, 1::2]
        R[1::2, ::2] = image[1::2, ::2]
        GR[1::2, 1::2] = image[1::2, 1::2]
    elif pattern == "BGGR":
        B[::2, ::2] = image[::2, ::2]
        GB[::2, 1::2] = image[::2, 1::2]
        GR[1::2, ::2] = image[1::2, ::2]
        R[1::2, 1::2] = image[1::2, 1::2]
    else:
        print("show failed")
        return False
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(rgb_img, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    print('show')


def test_case_fullsize():
    b = np.fromfile("CWF-MCC.raw", dtype="uint16")
    print("bshape", b.shape)
    print('%#x' % b[0])
    b.shape = [3024, 4032]
    out = b
    out = out / 1023.0
    raw_image_show_fullsize(out, 3024, 4032)


def test_case_thumbnail():
    b = np.fromfile('image\Input_4032_3024_RGGB.raw', dtype="uint16")
    print("b shape", b.shape)
    print('%#x' % b[0])
    b.shape = [3024, 4032]
    out = b
    out = out / 1023.0
    raw_image_show_thumbnail(out, 3024, 4032)


def test_case_fakecolor():
    b = np.fromfile("image\Input_4032_3024_RGGB.raw", dtype="uint16")
    print("b shape", b.shape)
    print('%#x' % b[0])
    b.shape = [3024, 4032]
    out = b
    out = out / 1023.0
    raw_image_show_fakecolor(out, 3024, 4032, "RGGB")


def test_case_3D():
    b = np.fromfile("image\Input_4032_3024_RGGB.raw", dtype="uint16")
    print("b shape", b.shape)
    print('%#x' % b[0])
    b.shape = [3024, 4032]
    c = b[0:100, 0:120]
    out = c
    out = out / 1023.0
    raw_image_show_3D(out, 100, 120)


if __name__ == "__main__":
    print('This is main of module')
    test_case_thumbnail()
