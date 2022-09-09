from struct import pack
import raw_image_show as rawshow
import numpy as np
import os
import cv2 as cv
import read_packed_word as readpackedword

def get_packed_word_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("packed_word"))
        #获取文件名
        file_list.extend(os.path.join("", file) for file in files if file.endswith("packed_word"))
  
    return file_list


if __name__ == "__main__":
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_packed_word_list=get_packed_word_file(current_working_dir)
    print(file_packed_word_list)
    # 循环查找packed_word的文件
    for file_packed_word in file_packed_word_list:
        print(file_packed_word)
        # 获取packed_word对应的信息
        packed_height = file_packed_word[file_packed_word.find('x') + 1:file_packed_word.find('.') - 5]
        packed_width = file_packed_word[file_packed_word.find('__') + 2:file_packed_word.find('x')]
        packed_bayer = file_packed_word[file_packed_word.find('.') - 1:file_packed_word.find('.')]
        packed_bit = file_packed_word[file_packed_word.find('.') - 4:file_packed_word.find('.') - 2]
        # 字符串转int
        packed_height = int(packed_height)
        packed_width = int(packed_width)
        packed_bayer = int(packed_bayer)
        packed_bit = int(packed_bit)
        print(packed_width)
        print(packed_height)
        print(packed_bayer)
        print(packed_bit)
        # 读取packed_word
        frame_raw = readpackedword.read_packed_word(file_packed_word, packed_height, packed_width, packed_bayer)
        frame_raw = frame_raw / 16
        raw_name=file_packed_word[:-12]
        raw_name=raw_name.replace('_10_','_12_')
        #cv.imwrite(f'{raw_name}bmp', frame_raw)
        #imwrite默认输出的是BGR图片，所以需要RGB转换未BGR再输出。
        frame_raw = frame_raw.astype(np.uint8)
        cv.imwrite(raw_name+'.bmp', cv.cvtColor(frame_raw,cv.COLOR_RGBA2BGRA))