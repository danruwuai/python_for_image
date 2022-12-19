#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import time
from multiprocessing import Process, Queue, Lock
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import read_unpack_raw as read_unpackraw
import threading
import queue

"""
class Task:
    def __init__(self, priority, description):
        self.priority = priority
        self.description = description
        # print("New Job:", description)
        return

    def __eq__(self, other):
        try:
            return self.priority == other.priority
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        try:
            return self.priority < other.priority
        except AttributeError:
            return NotImplemented
"""


def masks_Bayer(im, pattern):
    h, w = im.shape
    R = np.zeros((h, w))
    GR = np.zeros((h, w))
    GB = np.zeros((h, w))
    B = np.zeros((h, w))

    # 将对应位置的元素取出来
    if pattern in [3, "RGGB"]:
        R[::2, ::2] = 1
        GR[::2, 1::2] = 1
        GB[1::2, ::2] = 1
        B[1::2, 1::2] = 1
    elif pattern in [2, "GRBG"]:
        GR[::2, ::2] = 1
        R[::2, 1::2] = 1
        B[1::2, ::2] = 1
        GB[1::2, 1::2] = 1
    elif pattern in [1, "GBRG"]:
        GB[::2, ::2] = 1
        B[::2, 1::2] = 1
        R[1::2, ::2] = 1
        GR[1::2, 1::2] = 1
    elif pattern in [0, "BGGR"]:
        B[::2, ::2] = 1
        GB[::2, 1::2] = 1
        GR[1::2, ::2] = 1
        R[1::2, 1::2] = 1
    else:
        print("no match bayer")
        return False
    R_m = R
    G_m = GB + GR
    B_m = B
    return R_m, G_m, B_m


def blinnear(img, pattern):
    img = img.astype(np.float64)
    R_m, G_m, B_m = masks_Bayer(img, pattern)

    H_G = np.array(
        [[0, 1, 0],
         [1, 4, 1],
         [0, 1, 0]]) / 4
    H_RB = np.array(
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]]) / 4

    R = signal.convolve(img * R_m, H_RB, 'same')
    G = signal.convolve(img * G_m, H_G, 'same')
    B = signal.convolve(img * B_m, H_RB, 'same')
    h, w = img.shape
    result_img = np.zeros((h, w, 3))

    result_img[:, :, 0] = R
    result_img[:, :, 1] = G
    result_img[:, :, 2] = B
    del R_m, G_m, B_m, H_RB, H_G
    result_img = result_img.astype(np.uint16)
    return result_img


def AH_gradient(img, pattern):
    X = img
    Rm, Gm, Bm = masks_Bayer(img, pattern)
    # green
    Hg1 = np.array([0, 1, 0, -1, 0])
    Hg2 = np.array([-1, 0, 2, 0, -1])

    Hg1 = Hg1.reshape(1, -1)
    Hg2 = Hg2.reshape(1, -1)
    Hg1 = Hg1.astype(np.float64)
    Hg2 = Hg2.astype(np.float64)
    return (Rm + Gm) * (np.abs(signal.convolve(X, Hg1, 'same')) + np.abs(signal.convolve(X, Hg2, 'same')))


def AH_gradientX(img, pattern, q, lock):
    Ga = AH_gradient(img, pattern)

    try:
        lock.acquire()
        # q.put({"Hx": Ga}, block=True, timeout=3)
        q.put({"Hx": Ga})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return Ga


def AH_gradientY(img, pattern, q, lock):
    if pattern in [3, "RGGB"]:
        new_pattern = 3  # "RGGB"
    elif pattern in [2, "GRBG"]:
        new_pattern = 1  # "GBRG"
    elif pattern in [1, "GBRG"]:
        new_pattern = 2  # "GRBG"
    elif pattern in [0, "BGGR"]:
        new_pattern = 0  # "BGGR"
    else:
        print("no match bayer")
        return False
    new_img = img.T
    Ga = AH_gradient(new_img, new_pattern)
    new_Ga = Ga.T
    try:
        lock.acquire()
        # q.put({"Hy": new_Ga}, block=True, timeout=3)
        q.put({"Hy": new_Ga})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return new_Ga


# def AH_interpolate(img, pattern, gamma, max_value):
def AH_interpolate(img, pattern, gamma):
    X = img
    Rm, Gm, Bm = masks_Bayer(img, pattern)
    # green
    Hg1 = np.array([0, 1 / 2, 0, 1 / 2, 0])
    Hg2 = np.array([-1 / 4, 0, 1 / 2, 0, -1 / 4])
    Hg = Hg1 + Hg2 * gamma
    Hg = Hg.reshape(1, -1)
    G = Gm * X + (Rm + Bm) * signal.convolve(X, Hg, 'same')
    # Gy = Gy.reshape(1, -1)
    # res = signal.convolve(h, Gy, mode="same")
    # red / bule
    Hr = [[1 / 4, 1 / 2, 1 / 4], [1 / 2, 1, 1 / 2], [1 / 4, 1 / 2, 1 / 4]]
    R = G + signal.convolve(Rm * (X - G), Hr, 'same')
    B = G + signal.convolve(Bm * (X - G), Hr, 'same')
    """
    max_value = 4096
    R = np.clip(R, 0, max_value)
    G = np.clip(G, 0, max_value)
    B = np.clip(B, 0, max_value)
    """
    R[R < 0] = 0
    G[G < 0] = 0
    B[B < 0] = 0
    R = R.astype(np.uint16)
    G = G.astype(np.uint16)
    B = B.astype(np.uint16)
    return R, G, B


# def AH_interpolateX(img, pattern, gamma, max_value):
def AH_interpolateX(img, pattern, gamma, q, lock):
    h, w = img.shape
    Y = np.zeros((h, w, 3))
    # R, G, B = AH_interpolate(img, pattern, gamma, max_value)
    R, G, B = AH_interpolate(img, pattern, gamma)
    Y[:, :, 0] = R
    Y[:, :, 1] = G
    Y[:, :, 2] = B
    print("AH_interpolate")
    try:
        lock.acquire()
        # q.put({"Yx": Y}, block=True, timeout=3)
        q.put({"Yx": Y})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return Y


# def AH_interpolateY(img, pattern, gamma, max_value):
def AH_interpolateY(img, pattern, gamma, q, lock):
    h, w = img.shape
    Y = np.zeros((h, w, 3))
    if pattern in [3, "RGGB"]:
        new_pattern = 3  # "RGGB"
    elif pattern in [2, "GRBG"]:
        new_pattern = 1  # "GBRG"
    elif pattern in [1, "GBRG"]:
        new_pattern = 2  # "GRBG"
    elif pattern in [0, "BGGR"]:
        new_pattern = 0  # "BGGR"
    else:
        print("no match bayer")
        return False
    new_img = img.T
    # R, G, B = AH_interpolate(new_img, new_pattern, gamma, max_value)
    R, G, B = AH_interpolate(new_img, new_pattern, gamma)
    Y[:, :, 0] = R.T
    Y[:, :, 1] = G.T
    Y[:, :, 2] = B.T
    try:
        lock.acquire()
        # q.put({"Yy": Y}, block=True, timeout=3)
        q.put({"Yy": Y})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return Y


def MNballset(delta):
    index = delta
    H = np.zeros((index * 2 + 1, index * 2 + 1, (index * 2 + 1) ** 2))

    k = 0
    for i in range(-index, index + 1):
        for j in range(-index, index + 1):
            p = np.linalg.norm([i, j])
            H[index + 1, index + j, k] = p
            k = k + 1
    H = H[:, :, 0:k]
    return H


def MNparamA(YxLAB, YyLAB):
    X = YxLAB
    Y = YyLAB
    kernel_H1 = np.array([1, -1, 0])
    kernel_H1 = kernel_H1.reshape(1, -1)
    kernel_H2 = np.array([0, -1, 1])
    kernel_H2 = kernel_H2.reshape(1, -1)
    kernel_V1 = kernel_H1.reshape(1, -1).T
    kernel_V2 = kernel_H2.reshape(1, -1).T
    # xxx = np.abs(signal.convolve(X[:, :, 0], kernel_H1, 'same'))
    # yyy = np.abs(signal.convolve(X[:, :, 0], kernel_H2, 'same'))
    MNlock = threading.Lock()
    MNq = queue.Queue()
    name1 = 'X0_h1'
    name2 = 'X0_h2'
    name3 = 'Y0_v1'
    name4 = 'Y0_v2'
    name5 = 'X1_h1'
    name6 = 'X2_h1'
    name7 = 'X1_h2'
    name8 = 'X2_h2'
    name9 = 'Y1_v2'
    name10 = 'Y2_v2'
    name11 = 'Y1_v1'
    name12 = 'Y2_v1'
    t1 = threading.Thread(target=cal_convolve, args=(X[:, :, 0], kernel_H1, name1, MNq, MNlock))
    t2 = threading.Thread(target=cal_convolve, args=(X[:, :, 0], kernel_H2, name2, MNq, MNlock))
    t3 = threading.Thread(target=cal_convolve, args=(Y[:, :, 0], kernel_V1, name3, MNq, MNlock))
    t4 = threading.Thread(target=cal_convolve, args=(Y[:, :, 0], kernel_V2, name4, MNq, MNlock))
    t5 = threading.Thread(target=cal_convolve, args=(X[:, :, 1], kernel_H1, name5, MNq, MNlock))
    t6 = threading.Thread(target=cal_convolve, args=(X[:, :, 2], kernel_H1, name6, MNq, MNlock))
    t7 = threading.Thread(target=cal_convolve, args=(X[:, :, 1], kernel_H2, name7, MNq, MNlock))
    t8 = threading.Thread(target=cal_convolve, args=(X[:, :, 2], kernel_H2, name8, MNq, MNlock))
    t9 = threading.Thread(target=cal_convolve, args=(Y[:, :, 1], kernel_V2, name9, MNq, MNlock))
    t10 = threading.Thread(target=cal_convolve, args=(Y[:, :, 2], kernel_V2, name10, MNq, MNlock))
    t11 = threading.Thread(target=cal_convolve, args=(Y[:, :, 1], kernel_V1, name11, MNq, MNlock))
    t12 = threading.Thread(target=cal_convolve, args=(Y[:, :, 2], kernel_V1, name12, MNq, MNlock))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t9.start()
    t10.start()
    t11.start()
    t12.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    t9.join()
    t10.join()
    t11.join()
    t12.join()
    dict1 = {}
    for _ in range(MNq.qsize()):
        dict1.update(MNq.get())
    X0_h1 = dict1['X0_h1']
    X0_h2 = dict1['X0_h2']
    Y0_v1 = dict1['Y0_v1']
    Y0_v2 = dict1['Y0_v2']
    X1_h1 = dict1['X1_h1']
    X2_h1 = dict1['X2_h1']
    X1_h2 = dict1['X1_h2']
    X2_h2 = dict1['X2_h2']
    Y1_v2 = dict1['Y1_v2']
    Y2_v2 = dict1['Y2_v2']
    Y1_v1 = dict1['Y1_v1']
    Y2_v1 = dict1['Y2_v1']
    eLM1 = np.maximum(np.abs(X0_h1), np.abs(X0_h2),)
    eLM2 = np.maximum(np.abs(Y0_v1), np.abs(Y0_v2),)
    eL = np.minimum(eLM1, eLM2)
    eCx = np.maximum(X1_h1 ** 2 + X2_h1 ** 2, X1_h2 ** 2 + X2_h2 ** 2)
    eCy = np.maximum(Y1_v2 ** 2 + Y2_v2 ** 2, Y1_v1 ** 2 + Y2_v1 ** 2)
    eC = np.minimum(eCx, eCy)
    eL = eL
    eC = eC ** 0.5
    return eL, eC


# 计算相似度f
def MNhomogeneity(LAB_image, delta, epsilonL, epsilonC, name, q, lock):
    index = delta
    H = MNballset(delta)
    X = LAB_image
    epsilonC_sq = epsilonC ** 2
    h, w, c = LAB_image.shape
    K = np.zeros((h, w))
    kh, kw, kc = H.shape

    # 注意浮点数精度可能会有影响
    for i in range(kc):
        L = np.abs(signal.convolve(X[:, :, 0], H[:, :, i], 'same') - X[:, :, 0]) <= epsilonL  # level set
        C = ((signal.convolve(X[:, :, 1], H[:, :, i], 'same') - X[:, :, 1]) ** 2 + (
                    signal.convolve(X[:, :, 2], H[:, :, i], 'same') - X[:, :, 2]) ** 2) <= epsilonC_sq
        U = C & L  # metric neighborhold
        K = K + U  # homogeneity
    try:
        lock.acquire()
        # q.put({"Yy": Y}, block=True, timeout=3)
        q.put({name: K})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return K


# 去artifact
def MNartifact(R, G, B, iteartions):
    h, w = R.shape
    Rt = np.zeros((h, w, 8))
    Bt = np.zeros((h, w, 8))
    Grt = np.zeros((h, w, 4))
    Gbt = np.zeros((h, w, 4))
    kernel_1 = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
    kernel_2 = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
    kernel_3 = np.array([[0, 0, 1], [0, 0, 0], [0, 0, 0]])
    kernel_4 = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]])
    kernel_5 = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    kernel_6 = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])
    kernel_7 = np.array([[0, 0, 0], [0, 0, 0], [1, 0, 0]])
    kernel_8 = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]])
    kernel_9 = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 1]])

    for i in range(iteartions):
        Rt[:, :, 0] = signal.convolve(R - G, kernel_1, 'same')
        Rt[:, :, 1] = signal.convolve(R - G, kernel_2, 'same')
        Rt[:, :, 2] = signal.convolve(R - G, kernel_3, 'same')
        Rt[:, :, 3] = signal.convolve(R - G, kernel_4, 'same')
        Rt[:, :, 4] = signal.convolve(R - G, kernel_6, 'same')
        Rt[:, :, 5] = signal.convolve(R - G, kernel_7, 'same')
        Rt[:, :, 6] = signal.convolve(R - G, kernel_8, 'same')
        Rt[:, :, 7] = signal.convolve(R - G, kernel_9, 'same')

        Rm = np.median(Rt, axis=2)
        R = G + Rm

        Bt[:, :, 0] = signal.convolve(B - G, kernel_1, 'same')
        Bt[:, :, 1] = signal.convolve(B - G, kernel_2, 'same')
        Bt[:, :, 2] = signal.convolve(B - G, kernel_3, 'same')
        Bt[:, :, 3] = signal.convolve(B - G, kernel_4, 'same')
        Bt[:, :, 4] = signal.convolve(B - G, kernel_6, 'same')
        Bt[:, :, 5] = signal.convolve(B - G, kernel_7, 'same')
        Bt[:, :, 6] = signal.convolve(B - G, kernel_8, 'same')
        Bt[:, :, 7] = signal.convolve(B - G, kernel_9, 'same')

        Bm = np.median(Bt, axis=2)
        B = G + Bm

        Grt[:, :, 0] = signal.convolve(G - R, kernel_2, 'same')
        Grt[:, :, 1] = signal.convolve(G - R, kernel_4, 'same')
        Grt[:, :, 2] = signal.convolve(G - R, kernel_6, 'same')
        Grt[:, :, 3] = signal.convolve(G - R, kernel_8, 'same')

        Grm = np.median(Grt, axis=2)
        Gr = R + Grm

        Gbt[:, :, 0] = signal.convolve(G - B, kernel_2, 'same')
        Gbt[:, :, 1] = signal.convolve(G - B, kernel_4, 'same')
        Gbt[:, :, 2] = signal.convolve(G - B, kernel_6, 'same')
        Gbt[:, :, 3] = signal.convolve(G - B, kernel_8, 'same')

        Gbm = np.median(Gbt, axis=2)
        Gb = B + Gbm
        G = (Gr + Gb) / 2
    return R, G, B


def cal_convolve(in1, kernel, name, q, lock):
    out1 = signal.convolve(in1, kernel, 'same')
    print(name)
    try:
        lock.acquire()
        # q.put({"Yy": Y}, block=True, timeout=3)
        q.put({name: out1})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')


# adams hamilton
# def AH_demosaic(img, pattern, gamma=1, max_value=255):
def AH_demosaic(img, pattern, gamma=1):
    queueLock = threading.Lock()
    workQueue = queue.Queue()
    # 转换为float，便于后边计算
    img = img.astype(np.float64)
    print("AH demosic start")
    imgh, imgw = img.shape
    imgs = 10
    # X, Y方向插值
    # 扩展大小
    # Y= [X(n + 1:-1: 2, n + 1: -1:2, :)  X(n + 1: -1:2,:,:)
    # X(:, n + 1:-1:2,:)
    # X(end - 1: -1:end - n, n + 1: -1:2, :)  X(end -1:-1:end-n,:,:)
    f = np.pad(img, ((imgs, imgs), (imgs, imgs)), 'reflect')
    # Yx = AH_interpolateX(f, pattern, gamma, max_value)
    # Yy = AH_interpolateY(f, pattern, gamma, max_value)
    """
    Yx = AH_interpolateX(f, pattern, gamma)
    Yy = AH_interpolateY(f, pattern, gamma)
    Hx = AH_gradientX(f, pattern)
    Hy = AH_gradientY(f, pattern)
    """
    # 创建线程并初始化线程
    t1 = threading.Thread(target=AH_interpolateX, args=(f, pattern, gamma, workQueue, queueLock))
    t2 = threading.Thread(target=AH_interpolateY, args=(f, pattern, gamma, workQueue, queueLock))
    t3 = threading.Thread(target=AH_gradientX, args=(f, pattern, workQueue, queueLock))
    t4 = threading.Thread(target=AH_gradientY, args=(f, pattern, workQueue, queueLock))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    """
    print(Yx.description)
    print(Hy.description)
    print(Hx.description)
    print(Hx.description)
    """
    dict = {}
    dict.update(workQueue.get())
    dict.update(workQueue.get())
    dict.update(workQueue.get())
    dict.update(workQueue.get())
    Yx = dict["Yx"]
    Yy = dict["Yy"]
    Hx = dict["Hx"]
    Hy = dict["Hy"]
    # set output to Yy if Hy >= Hx
    bigger_index = np.where(Hy <= Hx)
    R = Yx[:, :, 0]
    G = Yx[:, :, 1]
    B = Yx[:, :, 2]
    Ry = Yy[:, :, 0]
    Gy = Yy[:, :, 1]
    By = Yy[:, :, 2]
    Rs = R
    Gs = G
    Bs = B
    Rs[bigger_index] = Ry[bigger_index]
    Gs[bigger_index] = Gy[bigger_index]
    Bs[bigger_index] = By[bigger_index]
    h, w = Rs.shape
    Y = np.zeros((h, w, 3))
    Y[:, :, 0] = Rs
    Y[:, :, 1] = Gs
    Y[:, :, 2] = Bs
    # 调整size和值的范围
    # Y = np.clip(Y, 0, max_value)
    resultY = Y[imgs:imgs + imgh, imgs:imgs + imgw, :]
    return resultY


# def AHD(img, pattern, delta=2, gamma=1, max_value=255):
def AHD(img, pattern, delta=2, gamma=1):
    queueLock = threading.Lock()
    workQueue = queue.Queue()
    print("AHD demosaic start")
    iterations = 2
    imgh, imgw = img.shape
    imgs = 10
    # X, Y方向插值
    # 扩展大小
    # Y= [X(n + 1:-1: 2, n + 1: -1:2, :)  X(n + 1: -1:2,:,:)
    # X(:, n + 1:-1:2,:)
    # X(end - 1: -1:end - n, n + 1: -1:2, :)  X(end -1:-1:end-n,:)
    f = np.pad(img, ((imgs, imgs), (imgs, imgs)), 'reflect')
    # Yx = AH_interpolateX(f, pattern, gamma, max_value)
    # Yy = AH_interpolateY(f, pattern, gamma, max_value)
    # Yx = AH_interpolateX(f, pattern, gamma)
    # Yy = AH_interpolateY(f, pattern, gamma)
    # 创建线程并初始化线程
    q = Queue()
    lock = Lock()
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    t1 = threading.Thread(target=AH_interpolateX, args=(f, pattern, gamma, workQueue, queueLock))
    t2 = threading.Thread(target=AH_interpolateY, args=(f, pattern, gamma, workQueue, queueLock))
    t1.start()
    t2.start()
    # t1.join()
    # t2.join()
    dict = {}
    dict.update(workQueue.get())
    dict.update(workQueue.get())
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    Yx = dict["Yx"]
    Yy = dict["Yy"]
    # 转LAB
    # YxLAB = RGB2LAB(Yx)
    # YyLAB = RGB2LAB(Yy)
    name1 = 'YxLAB'
    name2 = 'YyLAB'
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    t3 = threading.Thread(target=RGB2LAB, args=(Yx, name1, workQueue, queueLock))
    t4 = threading.Thread(target=RGB2LAB, args=(Yx, name2, workQueue, queueLock))
    t3.start()
    t4.start()
    # t3.join()
    # t4.join()
    dict.update(workQueue.get())
    dict.update(workQueue.get())
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    YxLAB = dict["YxLAB"]
    YyLAB = dict["YyLAB"]
    # 色彩差异的运算
    epsilonL, epsilonC = MNparamA(YxLAB, YyLAB)
    # Hx = MNhomogeneity(YxLAB, delta, epsilonL, epsilonC)
    # Hy = MNhomogeneity(YyLAB, delta, epsilonL, epsilonC)
    name3 = 'Hx'
    name4 = 'Hy'
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    obj0 = Process(target=MNhomogeneity, args=(YxLAB, delta, epsilonL, epsilonC, name3, q, lock))
    obj1 = Process(target=MNhomogeneity, args=(YyLAB, delta, epsilonL, epsilonC, name4, q, lock))
    obj0.start()
    obj1.start()
    # t5.join()
    # t6.join()
    dict.update(q.get())
    dict.update(q.get())
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    Hx = dict["Hx"]
    Hy = dict["Hy"]
    obj0.join()
    obj1.join()
    obj0.close()
    obj1.close()
    f_kernel = np.ones((3, 3))
    Hx = signal.convolve(Hx, f_kernel, 'same')
    Hy = signal.convolve(Hy, f_kernel, 'same')
    # 选择X, Y
    # set output initially to Yx
    R = Yx[:, :, 0]
    G = Yx[:, :, 1]
    B = Yx[:, :, 2]
    Ry = Yy[:, :, 0]
    Gy = Yy[:, :, 1]
    By = Yy[:, :, 2]
    bigger_index = np.where(Hy >= Hx)
    Rs = R
    Gs = G
    Bs = B
    Rs[bigger_index] = Ry[bigger_index]
    Gs[bigger_index] = Gy[bigger_index]
    Bs[bigger_index] = By[bigger_index]
    h, w = Rs.shape
    YT = np.zeros((h, w, 3))
    YT[:, :, 0] = Rs
    YT[:, :, 1] = Gs
    YT[:, :, 2] = Bs
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    # 去掉artifact
    Rsa, Gsa, Bsa = MNartifact(Rs, Gs, Bs, iterations)
    # R and B
    # values
    #
    Y = np.zeros((h, w, 3))
    Y[:, :, 0] = Rsa
    Y[:, :, 1] = Gsa
    Y[:, :, 2] = Bsa

    # 调整size和值的范畴
    # Y = np.clip(Y, 0, max_value)
    resultY = Y[imgs:imgs + imgh, imgs:imgs + imgw, :]
    print("++++++++++++++++++++++++++++++++++++++++", time.time())
    return resultY


# internal function
def labf(t):
    d = t ** (1 / 3)
    index = np.where(t <= 0.008856)
    d[index] = 7.787 * t[index] + 16 / 116
    return d


def RGB2LAB(X, name, q, lock):
    a = np.array([
        [3.40479, -1.537150, -0.498535],
        [-0.969256, 1.875992, 0.041556],
        [0.055648, -0.204043, 1.057311]])
    ai = np.linalg.inv(a)
    print(ai)
    h, w, c = X.shape
    R = X[:, :, 0]
    G = X[:, :, 1]
    B = X[:, :, 2]
    planed_R = R.flatten()
    planed_G = G.flatten()
    planed_B = B.flatten()
    planed_image = np.zeros((c, h * w))
    planed_image[0, :] = planed_R
    planed_image[1, :] = planed_G
    planed_image[2, :] = planed_B
    planed_lab = np.dot(ai, planed_image)
    planed_1 = planed_lab[0, :]
    planed_2 = planed_lab[1, :]
    planed_3 = planed_lab[2, :]
    L1 = np.reshape(planed_1, (h, w))
    L2 = np.reshape(planed_2, (h, w))
    L3 = np.reshape(planed_3, (h, w))
    result_lab = np.zeros((h, w, c))
    # color space conversion into LAB
    result_lab[:, :, 0] = 116 * labf(L2 / 255) - 16
    result_lab[:, :, 1] = 500 * (labf(L1 / 255) - labf(L2 / 255))
    result_lab[:, :, 2] = 200 * (labf(L2 / 255) - labf(L3 / 255))
    try:
        lock.acquire()
        # q.put({"Yy": Y}, block=True, timeout=3)
        q.put({name: result_lab})
        lock.release()
    except q.Full:
        print('任务%d: 队列已满，写入失败')
    return result_lab


def test_AHD_demosaic():
    pattern = 2
    bit = 12
    file_name = "011928646-0932-0935-mfll-iso-736-exp-20004-bfbld-raw__3264x2448_10_2.raw"
    maxvalue = 1023
    w = 3264
    h = 2448
    img = read_unpackraw.read_unpack_file(file_name, h, w, bit)
    result = AHD(img, pattern)
    # result = AH_demosaic(img, pattern)
    height, width = img.shape
    x = width / 100
    y = height / 100
    plt.figure(num='test', figsize=(x, y))
    plt.imshow(result / maxvalue, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    plt.show()
    return


if __name__ == '__main__':
    test_AHD_demosaic()
