
import cv2 as cv
import numpy as np



# region 辅助函数
# RGB2XYZ空间的系数矩阵
"""
M = np.array([[0.412453, 0.357580, 0.180423],
              [0.212671, 0.715160, 0.072169],
              [0.019334, 0.119193, 0.950227]])
"""
M = np.array([[0.433910, 0.376220, 0.189860],
              [0.212649, 0.715169, 0.072182],
              [0.017756, 0.109478, 0.872915]])


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
    for i in range(24):
        # cv获取的顺序位BGR，所以要转换为RGB
        color_data[i,0,2] =image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],0].mean()
        color_data[i,0,1] =image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],1].mean()
        color_data[i,0,0] =image[pt1[i][1]:pt2[i][1],pt1[i][0]:pt2[i][0],2].mean()
    if color_data.max() > 1:
        print(color_data/255)
    else:
        print(color_data)
        color_data = color_data * 255

    lab_data = RGB2Lab(color_data)
    print(lab_data)
    
    
"""
def RGB2LAB(X):
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
    return result_lab


# internal function
def labf(t):
    d = t ** (1 / 3)
    index = np.where(t <= 0.008856)
    d[index] = 7.787 * t[index] + 16 / 116
    return d
"""


# region RGB 转 Lab
# 像素值RGB转XYZ空间，pixel格式:(B,G,R)
# 返回XYZ空间下的值
def __rgb2xyz__(rgb):
    rgb = degamma_srgb(rgb, clip_range=[0, 255])
    rgb = rgb / 255.0
    h, w, c = rgb.shape
    R = rgb[:, :, 0]
    G = rgb[:, :, 1]
    B = rgb[:, :, 2]
    planed_R = R.flatten()
    planed_G = G.flatten()
    planed_B = B.flatten()
    planed_image = np.zeros((c, h * w))
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
    LAB = np.zeros(shape=(size,1,3))
    F_XYZ[0] = [f(x) for x in xyz[0]]
    F_XYZ[1] = [f(x) for x in xyz[1]]
    F_XYZ[2] = [f(x) for x in xyz[2]]
    L = np.zeros(size)
    for i in range(size):
        L[i] = 116 * F_XYZ[1,i] - 16 if xyz[1][i] > 0.008856 else 903.3 * xyz[1][i]
    a = 500 * (F_XYZ[0,] - F_XYZ[1,])
    b = 200 * (F_XYZ[1,] - F_XYZ[2,])
    print(L.shape, LAB[:,:,0].shape)
    LAB[:,:,0] = L.reshape(size,1)
    LAB[:,:,1] = a.reshape(size,1)
    LAB[:,:,2] = b.reshape(size,1)

    return LAB


def RGB2Lab(image):
    """
    RGB空间转Lab空间
    :param pixel: RGB空间像素值，格式：[G,B,R]
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


if __name__ == '__main__':
    image_file = 'TL84_1.jpg'
    image, pt1, pt2 = show_24_color(image_file)
    save_24_color_data(image, pt1, pt2)
