#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
import os, sys
from matplotlib import pyplot as plt
import numpy as np
from multiprocessing import Process

AAA_debug = [0, 0, 0xFF, 0xE6]
ISP_debug = [0xFF, 0xE7]


# DEBUG_EXIF_KEYID_AAA = 0xF0F1F200
# DEBUG_EXIF_KEYID_ISP = 0xF4F5F6F7
# DEBUG_PARSER_VERSION = 5
# AAA_DEBUG_KEYID = (DEBUG_EXIF_KEYID_AAA | DEBUG_PARSER_VERSION)
# AAA_Modulecount = [5, 0, 5, 0]


def get_jpg_tuning_ispinfo_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.endswith(
            "jpg") or file.endswith("tuning") or file.endswith(
                "ispinfo") and os.path.isfile(file)))

    return file_list


def load_jpg_tuning():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_exif_list = get_jpg_tuning_ispinfo_file(current_working_dir)
    # Exif 地址
    exif = current_working_dir + "/EXIF"
    # print(file_exif_list)
    if file_exif_list:
        if not os.path.exists('Result'):
            os.makedirs('Result')
    # 循环查找raw的文件
    for file_exif in file_exif_list:
        print("获取的文件：", file_exif)
        exif_name = file_exif + ".exif"
        dict_data, dict_info, exit_flag = import_exif_tuning(file_exif)
        if exit_flag == False:
            return False
        ae_debug(dict_data["ae_value_data"], dict_info, exif, exif_name)
        if dict_info["aaa_modulecount"] == 0x70005:
            ae_debug_data(dict_data["ae_debug_value_data"], exif_name)
        af_debug(dict_data["af_value_data"], dict_info, exif, exif_name)
        awb_debug(dict_data["awb_value_data"], dict_info, exif, exif_name)
        shading_debug(dict_data["shading_value_data"], dict_info, exif, exif_name)
        flash_debug(dict_data["flash_value_data"], dict_info, exif, exif_name)
        isp_debug(dict_data["isp_value_data"], dict_info, exif, exif_name)
        
        if dict_info["isp_modulecount"] != 0x30002:
            isp_p1reg_debug(dict_data["isp_p1reg_data"], dict_info, exif, exif_name)
            isp_p2reg_debug(dict_data["isp_p2reg_data"], dict_info, exif, exif_name)
            mfb_reg_debug(dict_data["mfb_reg_data"], dict_info, exif, exif_name)
            awb_data_debug_old(dict_data["awb_debug_data"], dict_info, exif_name)
        else:
            awb_data_debug_new(dict_data["awb_debug_data"], dict_info, exif_name)



def load_jpg_data(file):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    exif = current_working_dir + "/EXIF"
    print("获取的文件：", file)
    if not os.path.exists(exif):
        return None, None, None, False
    exif_name = file + "_awb.exif"
    dict_data, dict_info, exit_flag = import_exif_tuning(file)
    if exit_flag == False:
        return None, None, None, False

    dict_awb = awb_debug(dict_data["awb_value_data"], dict_info, exif, exif_name)
    if dict_info["isp_modulecount"] == 0x30002:
        dict_isp = isp_debug(dict_data["isp_value_data"], dict_info, exif, exif_name)
        return dict_awb, dict_isp, dict_info, True
    else:
        dict_p2reg = isp_p2reg_debug(dict_data["isp_p2reg_data"], dict_info, exif, exif_name)
        return dict_awb, dict_p2reg, dict_info, True


def import_exif_tuning(tuning_file_path):
    dict_info = {}
    dict_data = {}

    tuning_size = os.path.getsize(tuning_file_path)
    # print("tuning_size", tuning_size)
    tuning_file = np.fromfile(tuning_file_path, count=tuning_size, dtype="uint8")
    AAA_flag = False
    ISP_flag = False
    for i in range(tuning_size):
        if not AAA_flag and tuning_file[i] == AAA_debug[0] and tuning_file[i + 1] == \
                AAA_debug[1] and tuning_file[i + 2] == AAA_debug[2] and tuning_file[i + 3] == AAA_debug[3]:
            AAA_size = (int(tuning_file[i + 4]) << 8) + tuning_file[i + 5]
            # print("AAA_size", AAA_size)
            aaa_data = tuning_file[i + 6: i + 6 + AAA_size - 2]
            AAA_flag = True
            if tuning_file[i + 6 + AAA_size - 2] == ISP_debug[0] and tuning_file[i + 6 + AAA_size - 1] == ISP_debug[1]:
                ISP_size = (int(tuning_file[i + 6 + AAA_size]) << 8) + tuning_file[i + 6 + AAA_size + 1]
                # print("ISP_size", ISP_size)
                isp_data = tuning_file[i + 6 + AAA_size + 2:i + 6 + AAA_size + ISP_size]
                ISP_flag = True
        if not ISP_flag and tuning_file[i] == ISP_debug[0] and tuning_file[i + 1] == ISP_debug[1]:
            ISP_size = (int(tuning_file[i + 2]) << 8) + tuning_file[i + 3]
            # print("ISP_size", ISP_size)
            isp_data = tuning_file[i + 4:i + 4 + ISP_size - 2]
            ISP_flag = True
        if AAA_flag and ISP_flag:
            break
    if not AAA_flag:
        print("not exit AAA_exif")
    else:
        dict_info["aaa_debug_keyid"] = (int(aaa_data[3]) << 24) + (int(aaa_data[2]) << 16) + (int(aaa_data[1]) << 8) + (
            int(aaa_data[0]) << 0)
        # print("AAA_DEBUG_KEYID,", '%#x' % dict_info["aaa_debug_keyid"])
        dict_info["debug_parser_version"] = int(aaa_data[0])
        dict_info["aaa_modulecount"] = (int(aaa_data[7]) << 24) + (int(aaa_data[6]) << 16) + (int(aaa_data[5]) << 8) + (
            int(aaa_data[4]) << 0)
        # print("AAA_DEBUG_MODULE,", '%#x' % dict_info["aaa_modulecount"])
        dict_info["ae_debug_info_offset"] = (int(aaa_data[11]) << 24) + (int(aaa_data[10]) << 16) + (int(
            aaa_data[9]) << 8) + (int(aaa_data[8]) << 0)
        dict_info["af_debug_info_offset"] = (int(aaa_data[15]) << 24) + (int(aaa_data[14]) << 16) + (int(
            aaa_data[13]) << 8) + (int(aaa_data[12]) << 0)
        dict_info["flash_debug_info_offset"] = (int(aaa_data[19]) << 24) + (int(aaa_data[18]) << 16) + (int(
            aaa_data[17]) << 8) + (int(aaa_data[16]) << 0)
        dict_info["flicker_debug_info_offset"] = (int(aaa_data[23]) << 24) + (int(aaa_data[22]) << 16) + (int(
            aaa_data[21]) << 8) + (int(aaa_data[20]) << 0)
        dict_info["shading_debug_info_offset"] = (int(aaa_data[27]) << 24) + (int(aaa_data[26]) << 16) + (int(
            aaa_data[25]) << 8) + (int(aaa_data[24]) << 0)
        if dict_info["aaa_modulecount"] == 0x50005:
            dict_info["aaa_common_size"] = (int(aaa_data[31]) << 24) + (int(aaa_data[30]) << 16) + (int(
                aaa_data[29]) << 8) + (int(aaa_data[28]) << 0)
            aaa_common_data = aaa_data[32:32 + dict_info["aaa_common_size"] - 4]
        else:
            dict_info["ae_debug_data_offset"] = (int(aaa_data[31]) << 24) + (int(aaa_data[30]) << 16) + \
                                                (int(aaa_data[29]) << 8) + (int(aaa_data[28]) << 0)
            dict_info["string_debug_info_offset"] = (int(aaa_data[35]) << 24) + (int(aaa_data[34]) << 16) + \
                                                    (int(aaa_data[33]) << 8) + (int(aaa_data[32]) << 0)
            dict_info["aaa_common_size"] = (int(aaa_data[39]) << 24) + (int(aaa_data[38]) << 16) + (
                    int(aaa_data[37]) << 8) + (int(aaa_data[36]) << 0)
            aaa_common_data = aaa_data[40:40 + dict_info["aaa_common_size"] - 4]
        dict_info["ae_checksum"] = (int(aaa_common_data[3]) << 24) + (int(aaa_common_data[2]) << 16) + (
                int(aaa_common_data[1]) << 8) + (int(aaa_common_data[0]) << 0)
        dict_info["ae_ver"] = (int(aaa_common_data[5]) << 8) + (int(aaa_common_data[4]) << 0)
        dict_info["ae_sub"] = (int(aaa_common_data[7]) << 8) + (int(aaa_common_data[6]) << 0)
        print(dict_info["ae_ver"], dict_info["ae_sub"])
        dict_info["af_checksum"] = (int(aaa_common_data[3 + 32]) << 24) + (int(aaa_common_data[2 + 32]) << 16) + (
                int(aaa_common_data[1 + 32]) << 8) + (int(aaa_common_data[0 + 32]) << 0)
        dict_info["af_ver"] = (int(aaa_common_data[5 + 32]) << 8) + (int(aaa_common_data[4 + 32]) << 0)
        dict_info["af_sub"] = (int(aaa_common_data[7 + 32]) << 8) + (int(aaa_common_data[6 + 32]) << 0)
        dict_info["flash_checksum"] = (int(aaa_common_data[3 + 32 * 2]) << 24) + (
                int(aaa_common_data[2 + 32 * 2]) << 16) + (
                int(aaa_common_data[1 + 32 * 2]) << 8) + (int(aaa_common_data[0 + 32 * 2]) << 0)
        dict_info["flash_ver"] = (int(aaa_common_data[5 + 32 * 2]) << 8) + (int(aaa_common_data[4 + 32 * 2]) << 0)
        dict_info["flash_sub"] = (int(aaa_common_data[7 + 32 * 2]) << 8) + (int(aaa_common_data[6 + 32 * 2]) << 0)
        dict_info["flicker_checksum"] = (int(aaa_common_data[3 + 32 * 3]) << 24) + (
                int(aaa_common_data[2 + 32 * 3]) << 16) + (int(aaa_common_data[1 + 32 * 3]) << 8) + (
                                                int(aaa_common_data[0 + 32 * 3]) << 0)
        dict_info["flicker_ver"] = (int(aaa_common_data[5 + 32 * 3]) << 8) + (int(aaa_common_data[4 + 32 * 3]) << 0)
        dict_info["flicker_sub"] = (int(aaa_common_data[7 + 32 * 3]) << 8) + (int(aaa_common_data[6 + 32 * 3]) << 0)
        dict_info["shading_checksum"] = (int(aaa_common_data[3 + 32 * 4]) << 24) + (
                int(aaa_common_data[2 + 32 * 4]) << 16) + (int(aaa_common_data[1 + 32 * 4]) << 8) + (
                                                int(aaa_common_data[0 + 32 * 4]) << 0)
        dict_info["shading_ver"] = (int(aaa_common_data[5 + 32 * 4]) << 8) + (int(aaa_common_data[4 + 32 * 4]) << 0)
        dict_info["shading_sub"] = (int(aaa_common_data[7 + 32 * 4]) << 8) + (int(aaa_common_data[6 + 32 * 4]) << 0)
        # 获取AE value的值
        ae_tuning_data = aaa_data[dict_info["ae_debug_info_offset"]:dict_info["af_debug_info_offset"]]
        ae_tuning_size = dict_info["af_debug_info_offset"] - dict_info["ae_debug_info_offset"]
        ae_tuning_data = ae_tuning_data.astype("int32")
        # 获取AF value的值
        af_tuning_data = aaa_data[dict_info["af_debug_info_offset"]:dict_info["flash_debug_info_offset"]]
        af_tuning_size = dict_info["flash_debug_info_offset"] - dict_info["af_debug_info_offset"]
        af_tuning_data = af_tuning_data.astype("int32")
        # 获取Flash value的值
        flash_tuning_data = aaa_data[dict_info["flash_debug_info_offset"]:dict_info["flicker_debug_info_offset"]]
        flash_tuning_size = dict_info["flicker_debug_info_offset"] - dict_info["flash_debug_info_offset"]
        flash_tuning_data = flash_tuning_data.astype("int32")
        # 获取Flicker value的值
        flicker_tuning_data = aaa_data[dict_info["flicker_debug_info_offset"]:dict_info["shading_debug_info_offset"]]
        flicker_tuning_size = dict_info["shading_debug_info_offset"] - dict_info["flicker_debug_info_offset"]
        flicker_tuning_data = flicker_tuning_data.astype("int32")

        if dict_info["aaa_modulecount"] == 0x70005:
            # 获取Shading的值
            shading_tuning_data = aaa_data[dict_info["shading_debug_info_offset"]:dict_info["ae_debug_data_offset"]]
            shading_tuning_size = dict_info["ae_debug_data_offset"] - dict_info["shading_debug_info_offset"]
            shading_tuning_data = shading_tuning_data.astype("int32")

            ae_debug_data = aaa_data[dict_info["ae_debug_data_offset"]:dict_info["string_debug_info_offset"]]
            ae_debug_size = dict_info["string_debug_info_offset"] - dict_info["ae_debug_data_offset"]
            ae_debug_data = ae_debug_data.astype("int32")
        else:
            # 获取Shading的值
            shading_tuning_data = aaa_data[dict_info["shading_debug_info_offset"]:]
            shading_tuning_size = len(aaa_data) - dict_info["shading_debug_info_offset"]
            shading_tuning_data = shading_tuning_data.astype("int32")

        dict_data["ae_value_data"] = cal_aaa_value(ae_tuning_data, ae_tuning_size)
        # 获取AF value的值
        dict_data["af_value_data"] = cal_af_value(af_tuning_data, af_tuning_size)
        dict_data["shading_value_data"] = cal_aaa_value(shading_tuning_data, shading_tuning_size)
        dict_data["flash_value_data"] = cal_aaa_value(flash_tuning_data, flash_tuning_size)
        if dict_info["aaa_modulecount"] == 0x70005:
            dict_data["ae_debug_value_data"] = cal_ae_data_value(ae_debug_data, ae_debug_size)
    if not ISP_flag:
        print("not exit ISP_exif")
    else:
        dict_info["isp_debug_keyid"] = (int(isp_data[3]) << 24) + (int(isp_data[2]) << 16) + (int(isp_data[1]) << 8) + (
            int(isp_data[0]) << 0)
        # print("ISP_DEBUG_KEYID,", '%#x' % dict_info["isp_debug_keyid"])
        dict_info["isp_modulecount"] = (int(isp_data[7]) << 24) + (int(isp_data[6]) << 16) + (int(isp_data[5]) << 8) + (
            int(isp_data[4]) << 0)
        # print("ISP_DEBUG_MODULE,", '%#x' % dict_info["isp_modulecount"])
        dict_info["awb_debug_info_offset"] = (int(isp_data[11]) << 24) + (int(isp_data[10]) << 16) + (int(
            isp_data[9]) << 8) + (int(isp_data[8]) << 0)
        dict_info["isp_debug_info_offset"] = (int(isp_data[15]) << 24) + (int(isp_data[14]) << 16) + (int(
            isp_data[13]) << 8) + (int(isp_data[12]) << 0)
        if dict_info["isp_modulecount"] == 0x30002:
            dict_info["awb_debug_data_offset"] = (int(isp_data[19]) << 24) + (int(isp_data[18]) << 16) + (int(
                isp_data[17]) << 8) + (int(isp_data[16]) << 0)
            dict_info["isp_common_size"] = (int(isp_data[23]) << 24) + (int(isp_data[22]) << 16) + (int(
                isp_data[21]) << 8) + (int(isp_data[20]) << 0)
            isp_common_data = isp_data[24:24 + dict_info["isp_common_size"] - 4]
        else:
            dict_info["isp_p1reg_data_offset"] = (int(isp_data[19]) << 24) + (int(isp_data[18]) << 16) + (
                int(isp_data[17]) << 8) + (int(isp_data[16]) << 0)
            dict_info["isp_p2reg_data_offset"] = (int(isp_data[23]) << 24) + (int(isp_data[22]) << 16) + (
                int(isp_data[21]) << 8) + (int(isp_data[20]) << 0)
            dict_info["mfb_reg_info_offset"] = (int(isp_data[27]) << 24) + (int(isp_data[26]) << 16) + (
                int(isp_data[25]) << 8) + (int(isp_data[24]) << 0)
            dict_info["awb_debug_data_offset"] = (int(isp_data[31]) << 24) + (int(isp_data[30]) << 16) + (
                int(isp_data[29]) << 8) + (int(isp_data[28]) << 0)
            dict_info["isp_common_size"] = (int(isp_data[35]) << 24) + (int(isp_data[34]) << 16) + (int(
                isp_data[33]) << 8) + (int(isp_data[32]) << 0)
            isp_common_data = isp_data[36:36 + dict_info["isp_common_size"] - 4]
        dict_info["awb_checksum"] = (int(isp_common_data[3]) << 24) + (int(isp_common_data[2]) << 16) + (int(
            isp_common_data[1]) << 8) + (int(isp_common_data[0]) << 0)
        dict_info["awb_ver"] = (int(isp_common_data[5]) << 8) + (int(isp_common_data[4]) << 0)
        dict_info["awb_sub"] = (int(isp_common_data[7]) << 8) + (int(isp_common_data[6]) << 0)
        # print(dict_info["awb_ver"], dict_info["awb_sub"])

        dict_info["isp_checksum"] = (int(isp_common_data[3 + 32]) << 24) + (int(isp_common_data[2 + 32]) << 16) + (
            int(isp_common_data[1 + 32]) << 8) + (int(isp_common_data[0 + 32]) << 0)
        dict_info["isp_ver"] = (int(isp_common_data[5 + 32]) << 8) + (int(isp_common_data[4 + 32]) << 0)
        dict_info["isp_sub"] = (int(isp_common_data[7 + 32]) << 8) + (int(isp_common_data[6 + 32]) << 0)
        # print(dict_info["isp_ver"], dict_info["isp_sub"])
        # 获取AWB value的值
        awb_tuning_data = isp_data[dict_info["awb_debug_info_offset"]:dict_info["isp_debug_info_offset"]]
        awb_tuning_size = dict_info["isp_debug_info_offset"] - dict_info["awb_debug_info_offset"]
        awb_tuning_data = awb_tuning_data.astype("int32")

        if dict_info["isp_modulecount"] == 0x30002:
            # 获取ISP value的值
            isp_tuning_data = isp_data[dict_info["isp_debug_info_offset"]:dict_info["awb_debug_data_offset"]]
            isp_tuning_size = dict_info["awb_debug_data_offset"] - dict_info["isp_debug_info_offset"]
            isp_tuning_data = isp_tuning_data.astype("int32")

            # 获取awb_debug的值
            awb_debug_size = isp_data[dict_info["awb_debug_data_offset"]] + np.left_shift(
                isp_data[dict_info["awb_debug_data_offset"]] + 1, 8) + np.left_shift(
                    isp_data[dict_info["awb_debug_data_offset"]] + 2, 16) + np.left_shift(
                        isp_data[dict_info["awb_debug_data_offset"]] + 3, 24)
            awb_debug_data = isp_data[dict_info[
                                          "awb_debug_data_offset"]:dict_info["awb_debug_data_offset"] + awb_debug_size]
            awb_debug_data = awb_debug_data.astype("int32")
        else:
            # 获取ISP value的值
            isp_tuning_data = isp_data[dict_info["isp_debug_info_offset"]:dict_info["isp_p1reg_data_offset"]]
            isp_tuning_size = dict_info["isp_p1reg_data_offset"] - dict_info["isp_debug_info_offset"]
            isp_tuning_data = isp_tuning_data.astype("int32")

            isp_p1reg_data = isp_data[dict_info["isp_p1reg_data_offset"]:dict_info["isp_p2reg_data_offset"]]
            isp_p1reg_size = dict_info["isp_p2reg_data_offset"] - dict_info["isp_p1reg_data_offset"]
            isp_p1reg_data = isp_p1reg_data.astype("uint32")
            dict_info["isp_p1reg_TableSize"] = (isp_p1reg_data[0]) + np.left_shift(
                isp_p1reg_data[1], 8) + np.left_shift(isp_p1reg_data[2], 16) + np.left_shift(isp_p1reg_data[3], 24)
            dict_info["isp_p1reg_HwVersion"] = (isp_p1reg_data[4]) + np.left_shift(
                isp_p1reg_data[5], 8) + np.left_shift(isp_p1reg_data[6], 16) + np.left_shift(isp_p1reg_data[7], 24)
            isp_p1reg_data_new = isp_p1reg_data[8:(dict_info["isp_p1reg_TableSize"]-1) * 4]

            isp_p2reg_data = isp_data[dict_info["isp_p2reg_data_offset"]:dict_info["mfb_reg_info_offset"]]
            isp_p2reg_size = dict_info["mfb_reg_info_offset"] - dict_info["isp_p2reg_data_offset"]
            isp_p2reg_data = isp_p2reg_data.astype("uint32")
            dict_info["isp_p2reg_TableSize"] = (isp_p2reg_data[0]) + np.left_shift(
                isp_p2reg_data[1], 8) + np.left_shift(isp_p2reg_data[2], 16) + np.left_shift(isp_p2reg_data[3], 24)
            dict_info["isp_p2reg_HwVersion"] = (isp_p2reg_data[4]) + np.left_shift(
                isp_p2reg_data[5], 8) + np.left_shift(isp_p2reg_data[6], 16) + np.left_shift(isp_p2reg_data[7], 24)
            isp_p2reg_data_new = isp_p2reg_data[8:(dict_info["isp_p2reg_TableSize"] - 1) * 4]

            mfb_reg_data = isp_data[dict_info["mfb_reg_info_offset"]:dict_info["awb_debug_data_offset"]]
            mfb_reg_size = dict_info["awb_debug_data_offset"] - dict_info["mfb_reg_info_offset"]
            mfb_reg_data = mfb_reg_data.astype("uint32")
            dict_info["mfb_reg_TableSize"] = (mfb_reg_data[0]) + np.left_shift(mfb_reg_data[1], 8) + np.left_shift(
                mfb_reg_data[2], 16) + np.left_shift(mfb_reg_data[3], 24)
            dict_info["mfb_reg_HwVersion"] = (mfb_reg_data[4]) + np.left_shift(
                mfb_reg_data[5], 8) + np.left_shift(mfb_reg_data[6], 16) + np.left_shift(mfb_reg_data[7], 24)
            mfb_reg_data_new = mfb_reg_data[8:(dict_info["mfb_reg_TableSize"] - 1) * 4]

            awb_debug_size = (isp_data[dict_info["awb_debug_data_offset"]] + np.left_shift(
                isp_data[dict_info["awb_debug_data_offset"]] + 1, 8) + np.left_shift(
                    isp_data[dict_info["awb_debug_data_offset"]] + 2, 16) + np.left_shift(
                        isp_data[dict_info["awb_debug_data_offset"]] + 3, 24)).astype("uint32")
            awb_debug_data = isp_data[
                             dict_info["awb_debug_data_offset"]:dict_info["awb_debug_data_offset"] + awb_debug_size]
            awb_debug_data = awb_debug_data.astype("int32")

        if dict_info["isp_modulecount"] == 0x30002:
            dict_data["awb_value_data"] = cal_isp_value(awb_tuning_data, awb_tuning_size)
            dict_data["isp_value_data"] = cal_isp_value(isp_tuning_data, isp_tuning_size)
            dict_data["awb_debug_data"] = cal_isp_value(awb_debug_data, awb_debug_size)
        else:
            dict_data["awb_value_data"] = cal_aaa_value(awb_tuning_data, awb_tuning_size)
            dict_data["isp_value_data"] = cal_aaa_value(isp_tuning_data, isp_tuning_size)
            dict_data["isp_p1reg_data"] = cal_isp_value(isp_p1reg_data_new, (dict_info["isp_p1reg_TableSize"]-1)*4)
            dict_data["isp_p2reg_data"] = cal_isp_value(isp_p2reg_data_new, (dict_info["isp_p2reg_TableSize"]-1)*4)
            dict_data["mfb_reg_data"] = cal_isp_value(mfb_reg_data_new, (dict_info["mfb_reg_TableSize"]-1)*4)
            dict_data["awb_debug_data"] = cal_isp_value(awb_debug_data, awb_debug_size)
    if not ISP_flag and not AAA_flag:
        return None, None, False
    return dict_data, dict_info, True


def cal_aaa_value(tuning_data, tuning_size):
    # tuning_size转换为8的倍数
    tuning_size = tuning_size // 8 * 8
    value_data = (tuning_data[4:tuning_size:8]) + np.left_shift(tuning_data[5:tuning_size:8], 8) + np.left_shift(
        tuning_data[6:tuning_size:8], 16) + np.left_shift(tuning_data[7:tuning_size:8], 24)
    value_num = tuning_data[:tuning_size:8] + tuning_data[1:tuning_size:8] + tuning_data[2:tuning_size:8] +\
                tuning_data[3:tuning_size:8] + tuning_data[4:tuning_size:8] + tuning_data[5:tuning_size:8] +\
                tuning_data[6:tuning_size:8] + tuning_data[7:tuning_size:8]
    value_data = value_data.astype("int64")
    value_data[value_num == 0] = 0xfffffffff
    # print(value_data)
    size = len(value_data)
    # print(size)

    return value_data


def cal_af_value(af_tuning_data, af_tuning_size):
    value_data = np.zeros(shape=(2, af_tuning_size // 8)).astype("int32")
    value_data[0, ] = af_tuning_data[0:af_tuning_size:8] + np.left_shift(af_tuning_data[1:af_tuning_size:8], 8)
    value_data[1, ] = af_tuning_data[4:af_tuning_size:8] + np.left_shift(
        af_tuning_data[5:af_tuning_size:8], 8) + np.left_shift(af_tuning_data[6:af_tuning_size:8], 16) + np.left_shift(
        af_tuning_data[7:af_tuning_size:8], 24)
    return value_data


def cal_isp_value(tuning_data, tuning_size):
    return tuning_data[:tuning_size:4] + np.left_shift(tuning_data[1:tuning_size:4], 8) + np.left_shift(
        tuning_data[2:tuning_size:4], 16) + np.left_shift(tuning_data[3:tuning_size:4], 24)


def cal_ae_data_value(tuning_data, tuning_size):
    value_data = np.zeros((tuning_size - 2048) // 4 + 2048 // 2).astype("uint32")
    value_data[:1024] = tuning_data[:2048:2] + np.left_shift(tuning_data[1:2048:2], 8)
    value_data[1024:(tuning_size - 2048) // 4 + 2048 // 2] = (tuning_data[2048:tuning_size:4]) + np.left_shift(
        tuning_data[2048 + 1:tuning_size:4], 8) + np.left_shift(
        tuning_data[2048 + 2:tuning_size:4], 16) + np.left_shift(tuning_data[2048 + 3:tuning_size:4], 24)

    return value_data


def ae_debug(ae_value_data, dict_info, exif, exif_name):
    ae_version = exif + "/AE/AE_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info[
        "ae_ver"], dict_info["ae_sub"])
    print("ae_version", ae_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "w") as version_file:
        version_file.write('[AE] : %s\n' % (ae_version.split('/')[-1]))
    ae_tag_data = import_debug_data(ae_version)
    ae_size = len(ae_tag_data)
    ae_tag = np.array(ae_tag_data)
    ae_value_data = ae_value_data[:ae_size]
    dict_ae = dict(zip(ae_tag, ae_value_data))
    # print(dict_ae)
    save_ae_exif(dict_ae, dict_info, exif_name)
    return dict_ae


def save_ae_exif(dict_ae, dict_info, exif_name):
    with open('Result/' + exif_name, "w") as ae_file:
        ae_file.write('[AE]\n')
        i = 0
        data_5_5 = np.zeros(5 * 5).astype("uint32")
        data_15_15_y = np.zeros(15 * 15).astype("uint32")
        data_15_15_r = np.zeros(15 * 15).astype("uint32")
        data_15_15_g = np.zeros(15 * 15).astype("uint32")
        data_15_15_b = np.zeros(15 * 15).astype("uint32")
        data_15_15_overcnt = np.zeros(15 * 15).astype("uint32")
        data_hist_0 = np.zeros(128).astype("uint32")
        data_hist_1 = np.zeros(128).astype("uint32")
        data_hist_2 = np.zeros(128).astype("uint32")
        data_hist_3 = np.zeros(128).astype("uint32")
        if dict_info["debug_parser_version"] == 5:
            for key in dict_ae.keys():
                if dict_ae[key] == 0xfffffffff:
                    continue
                if key[0:15] == "AE_TAG_STAT_WIN":
                    data_5_5[i] = dict_ae[key]
                    i = i + 1
                    # print(data_5_5)
                    if i == 25:
                        i = 0

                if key[0:21] == "AE_TAG_STATRGBY15_WIN":
                    data_15_15_y[i] = np.bitwise_and(dict_ae[key], 0xFF)
                    data_15_15_b[i] = np.right_shift(np.bitwise_and(dict_ae[key], 0xFF00), 8)
                    data_15_15_g[i] = np.right_shift(np.bitwise_and(dict_ae[key], 0xFF0000), 16)
                    data_15_15_r[i] = np.right_shift(np.bitwise_and(dict_ae[key], 0xFF000000), 24)
                    i = i + 1
                    if i == 15 * 15:
                        i = 0
                if key[0:18] == "AE_TAG_OVERCNT_WIN":
                    data_15_15_overcnt[i] = dict_ae[key]
                    i = i + 1
                    if i == 15 * 15:
                        i = 0

                if key[0:22] == "AE_TAG_HIST0_INFO_BIN_":
                    if 19 < i < 40:
                        i = 40
                    elif 59 < i < 80:
                        i = 80
                    data_hist_0[i] = dict_ae[key]
                    i = i + 1
                    if i == 100:
                        i = 0

                if key[0:22] == "AE_TAG_HIST1_INFO_BIN_":
                    data_hist_1[i] = dict_ae[key]
                    i = i + 1
                    if i == 128:
                        i = 0

                if key[0:22] == "AE_TAG_HIST2_INFO_BIN_":
                    data_hist_2[i] = dict_ae[key]
                    i = i + 1
                    if i == 128:
                        i = 0

                if key[0:22] == "AE_TAG_HIST3_INFO_BIN_":
                    data_hist_3[i] = dict_ae[key]
                    i = i + 1
                    if i == 128:
                        i = 0

                ae_file.write('%56s:%13d | \n' % (key.ljust(56), dict_ae[key]))
            ae_file.write('\n')
            ae_file.write('[AE_Table]\n')

            ae_file.write('<<5x5>>\n')
            for i in range(5 * 5):
                ae_file.write(' %3s ' % (str(data_5_5[i]).ljust(3)))
                if (i + 1) % 5 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<15x15 Y>>\n')
            for i in range(15 * 15):
                ae_file.write(' %3s ' % str(data_15_15_y[i]).ljust(3))
                if (i + 1) % 15 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<15x15 R>>\n')
            for i in range(15 * 15):
                ae_file.write(' %3s ' % str(data_15_15_r[i]).ljust(3))
                if (i + 1) % 15 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<15x15 G>>\n')
            for i in range(15 * 15):
                ae_file.write(' %3s ' % str(data_15_15_g[i]).ljust(3))
                if (i + 1) % 15 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<15x15 B>>\n')
            for i in range(15 * 15):
                ae_file.write(' %3s ' % str(data_15_15_b[i]).ljust(3))
                if (i + 1) % 15 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<15x15 OverCnt>>\n')
            for i in range(15 * 15):
                ae_file.write(' %3s ' % str(data_15_15_overcnt[i]).ljust(3))
                if (i + 1) % 15 == 0:
                    ae_file.write('\n')
                    ae_file.write('\n')

            ae_file.write('<<HIST 0>>\n')
            for i in range(128):
                ae_file.write(' %6s ' % str(data_hist_0[i]).ljust(6))
                if (i + 1) % 16 == 0:
                    ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')

            ae_file.write('<<HIST 1>>\n')
            for i in range(128):
                ae_file.write(' %6s ' % str(data_hist_1[i]).ljust(6))
                if (i + 1) % 16 == 0:
                    ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')

            ae_file.write('<<HIST 2>>\n')
            for i in range(128):
                ae_file.write(' %6s ' % str(data_hist_2[i]).ljust(6))
                if (i + 1) % 16 == 0:
                    ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')

            ae_file.write('<<HIST 3>>\n')
            for i in range(128):
                ae_file.write(' %6s ' % str(data_hist_3[i]).ljust(6))
                if (i + 1) % 16 == 0:
                    ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')
            ae_file.write('\n')
            obj = Process(target=show_ae_data_old, args=(
                data_5_5, data_15_15_y, data_15_15_r, data_15_15_g, data_15_15_b, data_15_15_overcnt, 
                data_hist_0, data_hist_1, data_hist_2, data_hist_3))
            obj.start()
        else:
            for key in dict_ae.keys():
                if dict_ae[key] == 0xfffffffff:
                    continue
                    pass
                ae_file.write('%48s:%13d | \n' % (key.ljust(48), dict_ae[key]))


def ae_debug_data(ae_debug_data, exif_name):
    # 读取AE信息
    width_blk = ae_debug_data[4]
    height_blk = ae_debug_data[5]
    width_num = ae_debug_data[6]
    height_num = ae_debug_data[7]
    data_num = width_num * height_num
    # 读取block信息
    LE_R_16_12 = np.zeros(shape=(height_num, width_num)).astype("uint32")
    LE_G_16_12 = np.zeros(shape=(height_num, width_num)).astype("uint32")
    LE_B_16_12 = np.zeros(shape=(height_num, width_num)).astype("uint32")
    LE_Y_16_12 = np.zeros(shape=(height_num, width_num)).astype("uint32")

    for i in range(height_num):
        LE_R_16_12[i, 0:width_num] = ae_debug_data[i * width_num + 8:i * width_num + 8 + width_num]
        LE_G_16_12[i, 0:width_num] = ae_debug_data[256 + i * width_num + 8:256 + i * width_num + 8 + width_num]
        LE_B_16_12[i, 0:width_num] = ae_debug_data[512 + i * width_num + 8:512 + i * width_num + 8 + width_num]
        LE_Y_16_12[i, 0:width_num] = ae_debug_data[768 + i * width_num + 8:768 + i * width_num + 8 + width_num]

    # 读取histogram信息
    LE_RGB_MAX_hist = ae_debug_data[1024 + 4: 1024 + 4 + 256]
    LE_Y_hist = ae_debug_data[1024 + 256 + 4: 1024 + 256 + 4 + 256]
    SE_Y_hist = ae_debug_data[1024 + 256 * 2 + 4: 1024 + 256 * 2 + 4 + 256]
    obj = Process(target=show_ae_data_new, args=(
        LE_R_16_12, LE_G_16_12, LE_B_16_12, LE_Y_16_12, LE_RGB_MAX_hist, LE_Y_hist, SE_Y_hist, width_num, height_num))
    obj.start()

    with open('Result/' + exif_name, "a") as ae_file:
        ae_file.write('\n')
        ae_file.write('[AE_Table]\n')
        ae_file.write('<<16_12_LE_Y>>\n')

        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_Y_16_12[i // width_num, i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')

        ae_file.write('<<16_12_LE_R>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_R_16_12[i // width_num, i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')

        ae_file.write('<<16_12_LE_G>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_G_16_12[i // width_num, i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')

        ae_file.write('<<16_12_LE_B>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_B_16_12[i // width_num, i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')

        ae_file.write('<<LE_RGB_MAX>>\n')
        for i in range(width_num * width_num):
            ae_file.write(' %6s ' % str(LE_RGB_MAX_hist[i]).ljust(6))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
        ae_file.write('\n')
        ae_file.write('\n')

        ae_file.write('<<LE_Y>>\n')
        for i in range(width_num * width_num):
            ae_file.write(' %6s ' % str(LE_Y_hist[i]).ljust(6))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
        ae_file.write('\n')
        ae_file.write('\n')

        ae_file.write('<<SE_Y>>\n')
        for i in range(width_num * width_num):
            ae_file.write(' %6s ' % str(SE_Y_hist[i]).ljust(6))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
        ae_file.write('\n')
        ae_file.write('\n')
        ae_file.write('\n')
        ae_file.write('\n')


def show_ae_data_old(
    data_5_5, data_15_15_y, data_15_15_r, data_15_15_g, data_15_15_b, data_15_15_overcnt, 
    data_hist_0, data_hist_1, data_hist_2, data_hist_3):
    X0 = np.arange(0, 5)
    Y0 = np.arange(0, 5)
    X0, Y0 = np.meshgrid(X0, Y0)
    X1 = np.arange(0, 15)
    Y1 = np.arange(0, 15)
    X1, Y1 = np.meshgrid(X1, Y1)

    block_data_5_5 = np.zeros(shape=(5, 5)).astype("uint32")
    block_data_15_15_y = np.zeros(shape=(15, 15)).astype("uint32")
    block_data_15_15_r = np.zeros(shape=(15, 15)).astype("uint32")
    block_data_15_15_g = np.zeros(shape=(15, 15)).astype("uint32")
    block_data_15_15_b = np.zeros(shape=(15, 15)).astype("uint32")
    block_data_15_15_overcnt = np.zeros(shape=(15, 15)).astype("uint32")
    for i in range(5):
        block_data_5_5[i, 0:5] = data_5_5[i * 5:(i + 1) * 5]

    for i in range(15):
        block_data_15_15_y[i, 0:15] = data_15_15_y[i * 15:(i + 1) * 15]
        block_data_15_15_r[i, 0:15] = data_15_15_r[i * 15:(i + 1) * 15]
        block_data_15_15_g[i, 0:15] = data_15_15_g[i * 15:(i + 1) * 15]
        block_data_15_15_b[i, 0:15] = data_15_15_b[i * 15:(i + 1) * 15]
        block_data_15_15_overcnt[i, 0:15] = data_15_15_overcnt[i * 15:(i + 1) * 15]

    fig1, ax = plt.subplots(2, 3, figsize=(10, 4.5))
    ax[0][0].set_title('5 X 5', color='gray', loc="left")  # 设置标题
    ax[0][0].axis('off')
    ax[0][0] = fig1.add_subplot(2, 3, 1, projection='3d')
    ax[0][0].plot_wireframe(X0, Y0, block_data_5_5, rstride=1, cstride=1, color='gray')

    ax[0][1].set_title('15 X 15 Y', color='gray', loc="left")  # 设置标题
    ax[0][1].axis('off')
    ax[0][1] = fig1.add_subplot(2, 3, 2, projection='3d')
    ax[0][1].plot_wireframe(X1, Y1, block_data_15_15_y, rstride=1, cstride=1, color='gray')

    ax[0][2].set_title('15 X 15 R', color='r', loc="left")  # 设置标题
    ax[0][2].axis('off')
    ax[0][2] = fig1.add_subplot(2, 3, 3, projection='3d')
    ax[0][2].plot_wireframe(X1, Y1, block_data_15_15_r, rstride=1, cstride=1, color='r')

    ax[1][0].set_title('15 X 15 OverCnt', color='gray', loc="left")  # 设置标题
    ax[1][0].axis('off')
    ax[1][0] = fig1.add_subplot(2, 3, 4, projection='3d')
    ax[1][0].plot_wireframe(X1, Y1, block_data_15_15_overcnt, rstride=1, cstride=1, color='gray')

    ax[1][1].set_title('15 X 15 G', color='g', loc="left")  # 设置标题
    ax[1][1].axis('off')
    ax[1][1] = fig1.add_subplot(2, 3, 5, projection='3d')
    ax[1][1].plot_wireframe(X1, Y1, block_data_15_15_g, rstride=1, cstride=1, color='g')

    ax[1][2].set_title('15 X 15 Y', color='b', loc="left")  # 设置标题
    ax[1][2].axis('off')
    ax[1][2] = fig1.add_subplot(2, 3, 6, projection='3d')
    ax[1][2].plot_wireframe(X1, Y1, block_data_15_15_b, rstride=1, cstride=1, color='b')
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    plt.suptitle("Block", fontweight="bold")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    fig2, ax1 = plt.subplots(2, 2, figsize=(10, 4.5))
    ax1[0][0].bar(range(len(data_hist_0)), data_hist_0, color='gray')
    ax1[0][0].set_title('Hist 0 Flare', color='gray', loc="left")  # 设置标题

    ax1[0][1].bar(range(len(data_hist_1)), data_hist_1, color='gray')
    ax1[0][1].set_title('Hist 1 FullRGB', color='gray', loc="left")  # 设置标题

    ax1[1][0].bar(range(len(data_hist_2)), data_hist_2, color='gray')
    ax1[1][0].set_title('Hist 2 CentralY', color='gray', loc="left")  # 设置标题

    ax1[1][1].bar(range(len(data_hist_3)), data_hist_3, color='gray')
    ax1[1][1].set_title('Hist 3 FullY', color='gray', loc="left")  # 设置标题
    # print(data_hist_3)
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    plt.suptitle("Histogram", fontweight="bold")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.ion()
    plt.pause(20)
    # plt.show()
    plt.close()


def show_ae_data_new(
    LE_R_16_12, LE_G_16_12, LE_B_16_12, LE_Y_16_12, LE_RGB_MAX_hist, LE_Y_hist,
    SE_Y_hist, width_num, height_num):
    X = np.arange(0, width_num)
    Y = np.arange(0, height_num)
    # print(X,Y)
    X, Y = np.meshgrid(X, Y)
    # print(X, Y)
    fig1, ax = plt.subplots(2, 2, figsize=(10, 4.5))

    ax[0][0].set_title('LE_R', color='r', loc="left")  # 设置标题
    ax[0][0].axis('off')
    ax[0][0] = fig1.add_subplot(2, 2, 1, projection='3d')
    ax[0][0].plot_wireframe(X, Y, LE_R_16_12, rstride=1, cstride=1, color='r')

    ax[0][1].set_title('LE_G', color='g', loc="left")  # 设置标题
    ax[0][1].axis('off')
    ax[0][1] = fig1.add_subplot(2, 2, 2, projection='3d')
    ax[0][1].plot_wireframe(X, Y, LE_G_16_12, rstride=1, cstride=1, color='g')

    ax[1][0].set_title('LE_B', color='b', loc="left")  # 设置标题
    ax[1][0].axis('off')
    ax[1][0] = fig1.add_subplot(2, 2, 3, projection='3d')
    ax[1][0].plot_wireframe(X, Y, LE_B_16_12, rstride=1, cstride=1, color='b')

    ax[1][1].set_title('LE_Y', loc="left")  # 设置标题
    ax[1][1].axis('off')
    ax[1][1] = fig1.add_subplot(2, 2, 4, projection='3d')
    ax[1][1].plot_wireframe(X, Y, LE_Y_16_12, rstride=1, cstride=1, color='gray')
    plt.suptitle("Block", fontweight="bold")
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    fig2, ax1 = plt.subplots(3, figsize=(10, 4.5))
    ax1[0].bar(range(len(LE_RGB_MAX_hist)), LE_RGB_MAX_hist, color='gray')
    ax1[0].set_title('LE_RGB_MAX_hist', color='gray', loc="left")  # 设置标题

    ax1[1].bar(range(len(LE_Y_hist)), LE_Y_hist, color='gray')
    ax1[1].set_title('LE_Y_hist', color='gray', loc="left")  # 设置标题

    ax1[2].bar(range(len(SE_Y_hist)), SE_Y_hist, color='gray')
    ax1[2].set_title('SE_Y_hist', color='gray', loc="left")  # 设置标题
    plt.suptitle("Histogram", fontweight="bold")
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.ion()
    plt.pause(20)
    # plt.show()
    plt.close()


def af_debug(af_value_data, dict_info, exif, exif_name):
    af_version = exif + "/AF/AF_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info[
        "af_ver"], dict_info["af_sub"])
    print("af_version", af_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "a") as version_file:
        version_file.write('[AF] : %s\n' % (af_version.split('/')[-1]))
    af_tag_data = import_debug_data(af_version)
    af_size = np.arange(len(af_tag_data)).astype("str")
    af_tag = np.array(af_tag_data)
    # 将af_value_data转换为字符型np,由于srt会截取为U11，所以这里直接修改类型为U750
    af_value_data = af_value_data.astype("U750")
    dict_af = dict(zip(af_size, af_tag))
    # print(dict_af)
    size_y, size_num = af_value_data.shape
    for i in range(size_num):
        if i > 0 and af_value_data[0, i] == '0':
            break
        af_value_data[0, i] = str(dict_af[af_value_data[0, i]])
    af_data = af_value_data[:, 0:i]
    if dict_info["debug_parser_version"] > 5:
        save_af_new_exif(af_data, i, exif_name)
    else:
        save_af_exif(af_data, i, exif_name)
    return dict_af


def save_af_exif(af_data, num, exif_name):
    with open('Result/' + exif_name, "a") as af_file:
        # af_file.write('\n')
        af_file.write('[AF]\n')
        flag = 0
        for i in range(num):
            if af_data[0, i] in (
                "DP_IDX", "HANDLEAF_CNT", "FP_IDX", "FP_FOCUS_POS", "DP_FOCUS_POS",
                "CAF_TYPE", "HANDLEAF_EXIF_TIME", "NV_CAF_W", "NV_STEP_L"):
                af_file.write('\n')
            af_file.write('%28s:%13s | ' % (af_data[0, i].ljust(28), af_data[1, i]))
            if af_data[0, i] in (
                "NV_EN_LEFT_SH", "HANDLEAF_EXIF_TIME", "MGR_CURRENT_POS", "MGR_GYRO_SENSOR_Z", "NV_TEMP_ERROR",
                "SCN_ISO", "FP_FOCUS_POS", "SCN_AFMODE", "SCN_MIN_TH", "FD_STATUS", "SCN_ZOOM_Y", "SCN_WIN_H",
                "DP_ZOOM_Y", "DP_WIN_H", "MZ_WIN_NUM", "CAF_FIN_3P", "MGR_TG_H", "PL_MINAREA", "MZ_WIN_H",
                "MGR_CROP_WIN_H", "MGR_DZ_FACTOR", "MGR_BIN_H", "MGR_FOCUSING_WIN_H", "MGR_OTFD_WIN_H",
                "MGR_CENTER_WIN_H", "MGR_CMD_WIN_H", "MGR_PD_BUF_TYPE", "MGR_PD_SEN_TYPE", "MGR_LASER_VAL",
                "MGR_CURRENT_POS", "MGR_TS") or "DUAL_SYNC" in af_data[0, i]:
                af_file.write('\n')
            if af_data[0, i] in ("NV_FD", "NV_PL", "NV_AFV3", "NV_ZE", "NV_SC_ACCE", "NV_SC_GYRO"):
                flag = flag + 1
                if flag == 10:
                    flag = 0
                    af_file.write('\n')
                if flag == 9 and af_data[0, i] in ("NV_SC_ACCE", "NV_SC_GYRO"):
                    flag = 0
                    af_file.write('\n')
        af_file.write('\n')
        af_file.write('\n')


def save_af_new_exif(af_data, num, exif_name):
    with open('Result/' + exif_name, "a") as af_file:
        # af_file.write('\n')
        af_file.write('[AF]\n')
        flag = 0
        for i in range(num):
            if af_data[0, i] in (
                "DP_IDX", "HANDLEAF_CNT", "FP_IDX", "FP_FOCUS_POS", "DP_FOCUS_POS", "MGR_TG_W",
                "DP_FIN_3P", "HANDLEAF_EXIF_TIME", "NV_CAF_W", "NV_STEP_L", "SCN_AFMODE", "CALI_FOCUS_POS"):
                af_file.write('\n')
            af_file.write('%24s:%13s | ' % (af_data[0, i].ljust(24), af_data[1, i]))
            if af_data[0, i] in (
                "NV_EN_LEFT_SH", "HANDLEAF_EXIF_TIME", "MGR_CURRENT_POS", "MGR_GYRO_SENSOR_Z", "NV_TEMP_ERROR",
                "SCN_ISO", "FP_FOCUS_POS", "SCN_AFMODE", "SCN_MIN_TH", "FD_STATUS", "SCN_ZOOM_Y", "SCN_WIN_H",
                "DP_ZOOM_Y", "DP_WIN_H", "MZ_WIN_NUM", "CAF_FIN_3P", "MGR_TG_H", "FP_EXT_BIN", "MZ_WIN_H",
                "MGR_CROP_WIN_H", "MGR_DZ_FACTOR", "MGR_BIN_H", "MGR_FOCUSING_WIN_H", "MGR_OTFD_WIN_H",
                "MGR_CENTER_WIN_H", "MGR_CMD_WIN_H", "MGR_PD_BUF_TYPE", "MGR_PD_SEN_TYPE", "MGR_LASER_VAL",
                "MGR_CURRENT_POS", "CALI_FOCUS_POS") or "DUAL_SYNC" in af_data[0, i]:
                af_file.write('\n')
            if af_data[0, i] in ("SEEK_RESERVE12"):
                flag = flag + 1
                if flag == 16:
                    flag = 0
                    af_file.write('\n')
            if af_data[0, i] in ("NV_FD", "NV_PL", "NV_AFV3", "NV_ZE", "NV_SC_ACCE", "NV_SC_GYRO"):
                flag = flag + 1
                if flag == 10:
                    flag = 0
                    af_file.write('\n')
                if flag == 9 and af_data[0, i] in ("NV_SC_ACCE", "NV_SC_GYRO"):
                    flag = 0
                    af_file.write('\n')
        af_file.write('\n')
        af_file.write('\n')


def awb_debug(awb_value_data, dict_info, exif, exif_name):
    awb_version = exif + "/AWB/AWB_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info[
        "awb_ver"], dict_info["awb_sub"])
    print("awb_version", awb_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "a") as version_file:
        version_file.write('[AWB] : %s\n' % (awb_version.split('/')[-1]))
    awb_tag_data = import_debug_data(awb_version)
    awb_size = len(awb_tag_data)
    awb_tag = np.array(awb_tag_data)
    awb_value_data = awb_value_data[0:awb_size]
    dict_awb = dict(zip(awb_tag, awb_value_data))
    # print(dict_awb)
    save_awb_exif(dict_awb, dict_info, exif_name)
    return dict_awb


def save_awb_exif(dict_awb, dict_info, exif_name):
    with open('Result/' + exif_name, "a") as awb_file:
        awb_file.write('\n')
        awb_file.write('[AWB]\n')
        for key in dict_awb.keys():
            if dict_info["isp_modulecount"] == 0x30002:
                awb_file.write('%48s:%13d | \n' % (key.ljust(48), dict_awb[key]))
            else:
                if dict_awb[key] == 0xfffffffff:
                    continue
                awb_file.write('%52s:%13d | \n' % (key.ljust(52), dict_awb[key]))


def shading_debug(shading_value_data, dict_info, exif, exif_name):
    shading_version = exif + "/SHADING/SHADING_{}_{}_{}.h".format(dict_info[
        "debug_parser_version"], dict_info["shading_ver"], dict_info["shading_sub"])
    print("shading_version", shading_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "a") as version_file:
        version_file.write('[Shading] : %s\n' % (shading_version.split('/')[-1]))
    shading_tag_data = import_debug_data(shading_version)
    shading_size = len(shading_tag_data)
    shading_tag = np.array(shading_tag_data)
    shading_value_data = shading_value_data[0:shading_size]
    dict_shading = dict(zip(shading_tag, shading_value_data))
    # print(dict_shading)
    save_shading_exif(dict_shading, dict_info, exif_name)
    return dict_shading


def save_shading_exif(dict_shading, dict_info, exif_name):
    with open('Result/' + exif_name, "a") as shading_file:
        shading_file.write('\n')
        shading_file.write('[Shading]\n')
        for key in dict_shading.keys():
            if dict_shading[key] == 0xfffffffff:
                continue
            shading_file.write('%32s:%13d | \n' % (key.ljust(32), dict_shading[key]))
        shading_file.write('\n')


def flash_debug(flash_value_data, dict_info, exif, exif_name):
    flash_version = exif + "/STROBE/STROBE_{}_{}_{}.h".format(dict_info[
        "debug_parser_version"], dict_info["flash_ver"], dict_info["flash_sub"])
    print("flash_version", flash_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "a") as version_file:
        version_file.write('[Strobe] : %s\n' % (flash_version.split('/')[-1]))
    flash_tag_data = import_debug_data(flash_version)
    flash_size = len(flash_tag_data)
    flash_tag = np.array(flash_tag_data)
    flash_value_data = flash_value_data[0:flash_size]
    dict_flash = dict(zip(flash_tag, flash_value_data))
    # print(dict_flash)
    save_flash_exif(dict_flash, dict_info, exif_name)
    return dict_flash


def save_flash_exif(dict_flash, dict_info, exif_name):
    with open('Result/' + exif_name, "a") as flash_file:
        flash_file.write('\n')
        flash_file.write('\n')
        flash_file.write('[Strobe]\n')
        for key in dict_flash.keys():
            if dict_flash[key] == 0xfffffffff:
                continue
            flash_file.write('%28s:%13d | \n' % (key.ljust(28), dict_flash[key]))
        flash_file.write('\n')


def isp_debug(isp_value_data, dict_info, exif, exif_name):
    isp_version = exif + "/ISP/ISP_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info[
        "isp_ver"], dict_info["isp_sub"])
    print("isp_version", isp_version)
    with open('Result/' + exif_name.split('.')[0] + '.version', "a") as version_file:
        version_file.write('[ISP] : %s\n' % (isp_version.split('/')[-1]))
    isp_tag_data = import_debug_data(isp_version)
    isp_size = len(isp_tag_data)
    isp_tag = np.array(isp_tag_data)
    isp_value_data = isp_value_data[0:isp_size]
    dict_isp = dict(zip(isp_tag, isp_value_data))
    # print(dict_isp)
    save_isp_exif(dict_isp, dict_info, exif_name)
    return dict_isp


def save_isp_exif(dict_isp, dict_info, exif_name):
    with open('Result/' + exif_name, "a") as isp_file:
        isp_file.write('\n')
        isp_file.write('\n')
        isp_file.write('[ISP]\n')
        for key in dict_isp.keys():
            if dict_info["isp_modulecount"] == 0x30002:
                isp_file.write('%56s:%13d | \n' % (key.ljust(56), dict_isp[key]))
            else:
                if dict_isp[key] == 0xfffffffff:
                    continue
                isp_file.write('%36s:%13d | \n' % (key.ljust(36), dict_isp[key]))
        isp_file.write('\n')


def isp_p1reg_debug(p1_reg_data, dict_info, exif, exif_name):
    for root, dirs, files in os.walk(exif + "/ISP/ISP_HW_REG/"):
        for i in range(len(dirs)):
            if ('_' + str(dict_info["isp_p1reg_HwVersion"])) in dirs[i]:
                dict_info["isp_p1reg_version"] = dirs[i]
                flag = 1
                break
        if flag == 1:
            break

    isp_version = exif + "/ISP/ISP_HW_REG/{}/isp_reg_p1.json".format(dict_info["isp_p1reg_version"])
    print("isp_version", isp_version)
    if os.path.isfile(isp_version):
        pass
    else:
        return False
    reg_tag_data, reg_size = import_reg_data(isp_version, dict_info["isp_p1reg_TableSize"]-1)
    reg_data_tag = reg_tag_data[0:reg_size, 0, 0]
    reg_tag = np.array(reg_data_tag)
    p1_reg_data = p1_reg_data[0:reg_size]
    dict_p1reg = dict(zip(reg_tag, p1_reg_data))
    # print(dict_isp)
    save_p1reg_exif(dict_p1reg, dict_info, reg_tag_data, reg_size, exif_name)
    return dict_p1reg


def save_p1reg_exif(dict_p1reg, dict_info, reg_tag_data, reg_size, exif_name):
    with open('Result/' + exif_name, "a") as p1reg_file:
        p1reg_file.write('[ISP_HW_P1]\n')
        for i in range(reg_size):
            if "_no_exist" in reg_tag_data[i, 0, 0]:
                continue
            p1reg_file.write('%32s0x%08X : 0x%08X\n' % (
                reg_tag_data[i, 0, 0].ljust(32), int(reg_tag_data[i, 1, 0]), dict_p1reg[reg_tag_data[i, 0, 0]]))
            for j in range(1, 33):
                p1reg_file.write('    %31s[%2d:%2d] : %d\n' % (reg_tag_data[i, 0, j].ljust(31), int(
                    reg_tag_data[i, 1, j]), int(reg_tag_data[i, 2, j]), np.right_shift(
                    np.bitwise_and(dict_p1reg[reg_tag_data[i, 0, 0]], 2 ** (int(reg_tag_data[i, 2, j]) + 1) - 2 ** int(
                        reg_tag_data[i, 1, j])), int(reg_tag_data[i, 1, j]))))
                if int(reg_tag_data[i, 2, j]) == 31:
                    break

        p1reg_file.write('\n')
        p1reg_file.write('\n')


def isp_p2reg_debug(p2_reg_data, dict_info, exif, exif_name):
    for root, dirs, files in os.walk(exif + "/ISP/ISP_HW_REG/"):
        for i in range(len(dirs)):
            if ('_' + str(dict_info["isp_p2reg_HwVersion"])) in dirs[i]:
                dict_info["isp_p2reg_version"] = dirs[i]
                flag = 1
                break
        if flag == 1:
            break
    isp_version = exif + "/ISP/ISP_HW_REG/{}/isp_reg_p2.json".format(dict_info["isp_p2reg_version"])
    print("isp_version", isp_version)
    if os.path.isfile(isp_version):
        pass
    else:
        return False
    reg_tag_data, reg_size = import_reg_data(isp_version, dict_info["isp_p2reg_TableSize"]-1)
    reg_data_tag = reg_tag_data[0:reg_size, 0, 0]
    reg_tag = np.array(reg_data_tag)
    p2_reg_data = p2_reg_data[0:reg_size]
    dict_p2reg = dict(zip(reg_tag, p2_reg_data))
    # print(dict_isp)
    save_p2reg_exif(dict_p2reg, dict_info, reg_tag_data, reg_size, exif_name)
    return dict_p2reg


def save_p2reg_exif(dict_p2reg, dict_info, reg_tag_data, reg_size, exif_name):
    with open('Result/' + exif_name, "a") as p2reg_file:
        p2reg_file.write('[ISP_HW_P2]\n')
        for i in range(reg_size):
            if "_no_exist" in reg_tag_data[i, 0, 0]:
                continue
            p2reg_file.write('%44s0x%08X : 0x%08X\n' % (
                reg_tag_data[i, 0, 0].ljust(44), int(reg_tag_data[i, 1, 0]), dict_p2reg[reg_tag_data[i, 0, 0]]))
            for j in range(1, 33):
                if "0" == reg_tag_data[i, 0, j]:
                    break
                p2reg_file.write('    %43s[%2d:%2d] : %d\n' % (reg_tag_data[i, 0, j].ljust(43), int(
                    reg_tag_data[i, 1, j]), int(reg_tag_data[i, 2, j]), np.right_shift(
                    np.bitwise_and(dict_p2reg[reg_tag_data[i, 0, 0]], 2 ** (int(reg_tag_data[i, 2, j]) + 1) - 2 ** int(
                        reg_tag_data[i, 1, j])), int(reg_tag_data[i, 1, j]))))
                if int(reg_tag_data[i, 2, j]) == 31:
                    break

        p2reg_file.write('\n')
        p2reg_file.write('\n')


def mfb_reg_debug(mfb_reg_data, dict_info, exif, exif_name):

    isp_version = exif + "/ISP/ISP_HW_REG/{}/isp_reg_mfb.json".format(dict_info["isp_p1reg_version"])
    # print("isp_version", isp_version)
    if os.path.isfile(isp_version):
        pass
    else:
        return False
    reg_tag_data, reg_size = import_reg_data(isp_version, dict_info["mfb_reg_TableSize"] - 1)
    reg_data_tag = reg_tag_data[0:reg_size, 0, 0]
    reg_tag = np.array(reg_data_tag)
    mfb_reg_data = mfb_reg_data[0:reg_size]
    dict_mfb_reg = dict(zip(reg_tag, mfb_reg_data))
    # print(dict_isp)
    save_mfb_reg_exif(dict_mfb_reg, dict_info, reg_tag_data, reg_size, exif_name)
    return dict_mfb_reg


def save_mfb_reg_exif(dict_mfb_reg, dict_info, reg_tag_data, reg_size, exif_name):
    with open('Result/' + exif_name, "a") as mfb_reg_file:
        mfb_reg_file.write('[ISP_HW_MFB]\n')
        for i in range(reg_size):
            if "_no_exist" in reg_tag_data[i, 0, 0]:
                continue
            mfb_reg_file.write('%32s0x%08X : 0x%08X\n' % (
                reg_tag_data[i, 0, 0].ljust(32), int(reg_tag_data[i, 1, 0]), dict_mfb_reg[reg_tag_data[i, 0, 0]]))
            for j in range(1, 33):
                mfb_reg_file.write('    %31s[%2d:%2d] : %d\n' % (reg_tag_data[i, 0, j].ljust(31), int(
                    reg_tag_data[i, 1, j]), int(reg_tag_data[i, 2, j]), np.right_shift(
                    np.bitwise_and(dict_mfb_reg[reg_tag_data[i, 0, 0]], 2 ** (int(reg_tag_data[i, 2, j]) + 1) - 2**int(
                        reg_tag_data[i, 1, j])), int(reg_tag_data[i, 1, j]))))
                if int(reg_tag_data[i, 2, j]) == 31:
                    break

        mfb_reg_file.write('\n')
        mfb_reg_file.write('\n')


# awb_debug_data数据
"""
      int32_t i4Size;             /*!< sizeof(AWB_DEBUG_DATA_T) */
      int32_t i4IsAWBAutoMode;    /*!< Is AWB auto mode, 0: false, 1: true */
      int32_t i4IsStrobeFired;    /*!< Is strobe fired, 0: strobe is not fired ==> do not draw light area of strobe */
      int32_t i4ParentBlkNum_X;   /*!< Parent block number */
      int32_t i4ParentBlkNum_Y;   /*!< Parent block number */
      int32_t i4SensorWidth;      /*!< Sensor dimension */
      int32_t i4SensorHeight;     /*!< Sensor dimension */
      int32_t i4OffsetH;          /*!< horizontal and vertical Offset of the first parent block (upper left) */
      int32_t i4OffsetV;          /*!< horizontal and vertical Offset of the first parent block (upper left) */
      int32_t i4ParentBlkWidth;   /*!< Parent block info */
      int32_t i4ParentBlkHeight;  /*!< Parent block info */
      # (4 + 4 + 4 + 1 + 1) * 24 x 18 = 6048 bytes
      int32_t sum_r[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // R summation of specified light source of specified parent block
      int32_t sum_g[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // G summation of specified light source of specified parent block
      int32_t sum_b[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // B summation of specified light source of specified parent block
      int8_t child_blk_num[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // Child block number of specified light source of specified parent block
      int8_t light[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // Light source of specified parent block
      int32_t i4CentralX; /*!< XY coordinate as the central point of debug image, D65 */
      int32_t i4CentralY; /*!< XY coordinate as the central point of debug image, D65 */
      int32_t i4Cos;      /*!< Rotation matrix */
      int32_t i4Sin;      /*!< Rotation matrix */
      int32_t i4RightBound_Strobe;    /*!< Strobe light area */
      int32_t i4LeftBound_Strobe;     /*!< Strobe light area */
      int32_t i4UpperBound_Strobe;    /*!< Strobe light area */
      int32_t i4LowerBound_Strobe;    /*!< Strobe light area */
      int32_t i4RightBound_Tungsten;  /*!< Tungsten light area */
      int32_t i4LeftBound_Tungsten;   /*!< Tungsten light area */
      int32_t i4UpperBound_Tungsten;  /*!< Tungsten light area */
      int32_t i4LowerBound_Tungsten;  /*!< Tungsten light area */
      int32_t i4RightBound_WarmFluorescent;   /*!< Warm fluorescent light area */
      int32_t i4LeftBound_WarmFluorescent;    /*!< Warm fluorescent light area */
      int32_t i4UpperBound_WarmFluorescent;   /*!< Warm fluorescent light area */
      int32_t i4LowerBound_WarmFluorescent;   /*!< Warm fluorescent light area */
      int32_t i4RightBound_Fluorescent;   /*!< Fluorescent light area */
      int32_t i4LeftBound_Fluorescent;    /*!< Fluorescent light area */
      int32_t i4UpperBound_Fluorescent;   /*!< Fluorescent light area */
      int32_t i4LowerBound_Fluorescent;   /*!< Fluorescent light area */
      int32_t i4RightBound_CWF;       /*!< CWF light area */
      int32_t i4LeftBound_CWF;        /*!< CWF light area */
      int32_t i4UpperBound_CWF;       /*!< CWF light area */
      int32_t i4LowerBound_CWF;       /*!< CWF light area */
      int32_t i4RightBound_Daylight;  /*!< Daylight light area */
      int32_t i4LeftBound_Daylight;   /*!< Daylight light area */
      int32_t i4UpperBound_Daylight;  /*!< Daylight light area */
      int32_t i4LowerBound_Daylight;  /*!< Daylight light area */
      int32_t i4RightBound_Shade;     /*!< Shade light area */
      int32_t i4LeftBound_Shade;      /*!< Shade light area */
      int32_t i4UpperBound_Shade;     /*!< Shade light area */
      int32_t i4LowerBound_Shade;     /*!< Shade light area */
      int32_t i4RightBound_DaylightFluorescent;   /*!< Daylight fluorescent light area */
      int32_t i4LeftBound_DaylightFluorescent;    /*!< Daylight fluorescent light area */
      int32_t i4UpperBound_DaylightFluorescent;   /*!< Daylight fluorescent light area */
      int32_t i4LowerBound_DaylightFluorescent;   /*!< Daylight fluorescent light area */
"""


# awb_data_debug分析
def awb_data_debug_new(awb_debug_data, dict_info, exif_name):
    dict_awb_debug = {}
    dict_awb_debug["size"] = awb_debug_data[0]
    dict_awb_debug["is_awb_auto_mode"] = awb_debug_data[1]  # 1:auto mode
    dict_awb_debug["is_strobe_fired"] = awb_debug_data[2]  # 0:strobe is not fired
    dict_awb_debug["parent_blk_num_x"] = awb_debug_data[3]
    dict_awb_debug["parent_blk_num_y"] = awb_debug_data[4]
    dict_awb_debug["sensor_width"] = awb_debug_data[5]
    dict_awb_debug["sensor_height"] = awb_debug_data[6]
    dict_awb_debug["offset_h"] = awb_debug_data[7]
    dict_awb_debug["offset_v"] = awb_debug_data[8]
    dict_awb_debug["parent_blk_width"] = awb_debug_data[9]
    dict_awb_debug["parent_blk_height"] = awb_debug_data[10]
    parent_blk_num = dict_awb_debug["parent_blk_num_y"] * dict_awb_debug["parent_blk_num_x"]
    sum_r = np.zeros(parent_blk_num).astype("uint32")
    sum_g = np.zeros(parent_blk_num).astype("uint32")
    sum_b = np.zeros(parent_blk_num).astype("uint32")
    sum_rgblight = np.zeros(shape=(dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"], 4))
    sum_r[::2] = np.bitwise_and(awb_debug_data[11:11 + parent_blk_num // 2], 0xFFFF)
    sum_r[1::2] = np.right_shift(np.bitwise_and(awb_debug_data[11:11 + parent_blk_num // 2], 0xFFFF0000), 16)
    sum_r.shape = [dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_r"] = sum_r
    sum_g[::2] = np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2: 11 + parent_blk_num // 2 * 2], 0xFFFF)
    sum_g[1::2] = np.right_shift(np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2: 11 + parent_blk_num // 2 * 2], 0xFFFF0000), 16)
    sum_g.shape = [dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_g"] = sum_g
    sum_b[::2] = np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 2: 11 + parent_blk_num // 2 * 3], 0xFFFF)
    sum_b[1::2] = np.right_shift(np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 2: 11 + parent_blk_num // 2 * 3], 0xFFFF0000), 16)
    sum_b.shape = [dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_b"] = sum_b
    sum_rgblight[:, :, 0] = sum_r
    sum_rgblight[:, :, 1] = sum_g
    sum_rgblight[:, :, 2] = sum_b
    obj = Process(target=show_awb_debug_data, args=(sum_rgblight[:, :, 0:3], dict_awb_debug["parent_blk_num_x"], dict_awb_debug[
        "parent_blk_num_y"], 8))
    obj.start()
    
    light = np.zeros(parent_blk_num).astype("uint32")
    light[::4] = np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 3:11 + parent_blk_num // 2 * 3 + parent_blk_num // 4], 0xFF)
    light[1::4] = np.right_shift(np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 3:11 + parent_blk_num // 2 * 3 + parent_blk_num // 4], 0xFF00), 8)
    light[2::4] = np.right_shift(np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 3:11 + parent_blk_num // 2 * 3 + parent_blk_num // 4], 0xFF0000), 16)
    light[3::4] = np.right_shift(np.bitwise_and(awb_debug_data[11 + parent_blk_num // 2 * 3:11 + parent_blk_num // 2 * 3 + parent_blk_num // 4], 0xFF000000), 24)
    light.shape = [dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"]]
    sum_rgblight[:, :, 3] = light
    dict_awb_debug["sum_rgblight"] = sum_rgblight
    dict_awb_debug["light"] = light
    blk_num_size = (4 + 4 + 4 + 1 + 1) * 24 * 18 // 4
    dict_awb_debug["central_x"] = awb_debug_data[11 + blk_num_size]
    dict_awb_debug["central_y"] = awb_debug_data[11 + blk_num_size + 1]
    dict_awb_debug["cos"] = awb_debug_data[11 + blk_num_size + 2]
    dict_awb_debug["sin"] = awb_debug_data[11 + blk_num_size + 3]
    dict_awb_debug["right_bound_strobe"] = awb_debug_data[11 + blk_num_size + 4]
    dict_awb_debug["left_bound_strobe"] = awb_debug_data[11 + blk_num_size + 5]
    dict_awb_debug["upper_bound_strobe"] = awb_debug_data[11 + blk_num_size + 6]
    dict_awb_debug["lower_bound_strobe"] = awb_debug_data[11 + blk_num_size + 7]    
    dict_awb_debug["right_bound_tungsten"] = awb_debug_data[11 + blk_num_size + 8]
    dict_awb_debug["left_bound_tungsten"] = awb_debug_data[11 + blk_num_size + 9]
    dict_awb_debug["upper_bound_tungsten"] = awb_debug_data[11 + blk_num_size + 10]
    dict_awb_debug["lower_bound_tungsten"] = awb_debug_data[11 + blk_num_size + 11]
    dict_awb_debug["right_bound_warmfluorescent"] = awb_debug_data[11 + blk_num_size + 12]
    dict_awb_debug["left_bound_warmfluorescent"] = awb_debug_data[11 + blk_num_size + 13]
    dict_awb_debug["upper_bound_warmfluorescent"] = awb_debug_data[11 + blk_num_size + 14]
    dict_awb_debug["lower_bound_warmfluorescent"] = awb_debug_data[11 + blk_num_size + 15] 
    dict_awb_debug["right_bound_fluorescent"] = awb_debug_data[11 + blk_num_size + 16]
    dict_awb_debug["left_bound_fluorescent"] = awb_debug_data[11 + blk_num_size + 17]
    dict_awb_debug["upper_bound_fluorescent"] = awb_debug_data[11 + blk_num_size + 18]
    dict_awb_debug["lower_bound_fluorescent"] = awb_debug_data[11 + blk_num_size + 19] 
    dict_awb_debug["right_bound_cwf"] = awb_debug_data[11 + blk_num_size + 20]
    dict_awb_debug["left_bound_cwf"] = awb_debug_data[11 + blk_num_size + 21]
    dict_awb_debug["upper_bound_cwf"] = awb_debug_data[11 + blk_num_size + 22]
    dict_awb_debug["lower_bound_cwf"] = awb_debug_data[11 + blk_num_size + 23] 
    dict_awb_debug["right_bound_daylight"] = awb_debug_data[11 + blk_num_size + 24]
    dict_awb_debug["left_bound_daylight"] = awb_debug_data[11 + blk_num_size + 25]
    dict_awb_debug["upper_bound_daylight"] = awb_debug_data[11 + blk_num_size + 26]
    dict_awb_debug["lower_bound_daylight"] = awb_debug_data[11 + blk_num_size + 27] 
    dict_awb_debug["right_bound_shade"] = awb_debug_data[11 + blk_num_size + 28]
    dict_awb_debug["left_bound_shade"] = awb_debug_data[11 + blk_num_size + 29]
    dict_awb_debug["upper_bound_shade"] = awb_debug_data[11 + blk_num_size + 30]
    dict_awb_debug["lower_bound_shade"] = awb_debug_data[11 + blk_num_size + 31] 
    dict_awb_debug["right_bound_daylightfluorescent"] = awb_debug_data[11 + blk_num_size + 32]
    dict_awb_debug["left_bound_daylightfluorescent"] = awb_debug_data[11 + blk_num_size + 33]
    dict_awb_debug["upper_bound_daylightfluorescent"] = awb_debug_data[11 + blk_num_size + 34]
    dict_awb_debug["lower_bound_daylightfluorescent"] = awb_debug_data[11 + blk_num_size + 35]
    
    return dict_awb_debug


"""
      MINT32 i4Size; // sizeof(AWB_DEBUG_DATA_T)
      // Is AWB auto mode
      MINT32 i4IsAWBAutoMode; // 0: false, 1: true
      // Is strobe fired
      MINT32 i4IsStrobeFired; // 0: strobe is not fired ==> do not draw light area of strobe
      // Parent block number
      MINT32 i4ParentBlkNum_X;
      MINT32 i4ParentBlkNum_Y;
      // Sensor dimension
      MINT32 i4SensorWidth;
      MINT32 i4SensorHeight;
      // horizontal and vertical Offset of the first parent block (upper left)
      MINT32 i4OffsetH;
      MINT32 i4OffsetV;
      // Parent block info
      MINT32 i4ParentBlkWidth;
      MINT32 i4ParentBlkHeight;
  	MINT32 i4SumR[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // R summation of specified light source of specified parent block
  	MINT32 i4SumG[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // G summation of specified light source of specified parent block
  	MINT32 i4SumB[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // B summation of specified light source of specified parent block
  	MINT32 i4ChildBlkNum[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // Child block number of specified light source of specified parent block
  	MINT32 i4Light[DBG_AWB_PARENT_BLK_NUM_MAX_Y][DBG_AWB_PARENT_BLK_NUM_MAX_X]; // Light source of specified parent block
      // XY coordinate as the central point of debug image
      MINT32 i4CentralX; // D65
      MINT32 i4CentralY; // D65
      // Rotation matrix
      MINT32 i4Cos;
      MINT32 i4Sin;
      // Strobe light area
      MINT32 i4RightBound_Strobe;
      MINT32 i4LeftBound_Strobe;
      MINT32 i4UpperBound_Strobe;
      MINT32 i4LowerBound_Strobe;
      // Tungsten light area
      MINT32 i4RightBound_Tungsten;
      MINT32 i4LeftBound_Tungsten;
      MINT32 i4UpperBound_Tungsten;
      MINT32 i4LowerBound_Tungsten;
      // Warm fluorescent light area
      MINT32 i4RightBound_WarmFluorescent;
      MINT32 i4LeftBound_WarmFluorescent;
      MINT32 i4UpperBound_WarmFluorescent;
      MINT32 i4LowerBound_WarmFluorescent;
      // Fluorescent light area
      MINT32 i4RightBound_Fluorescent;
      MINT32 i4LeftBound_Fluorescent;
      MINT32 i4UpperBound_Fluorescent;
      MINT32 i4LowerBound_Fluorescent;
      // CWF light area
      MINT32 i4RightBound_CWF;
      MINT32 i4LeftBound_CWF;
      MINT32 i4UpperBound_CWF;
      MINT32 i4LowerBound_CWF;
      // Daylight light area
      MINT32 i4RightBound_Daylight;
      MINT32 i4LeftBound_Daylight;
      MINT32 i4UpperBound_Daylight;
      MINT32 i4LowerBound_Daylight;
      // Shade light area
      MINT32 i4RightBound_Shade;
      MINT32 i4LeftBound_Shade;
      MINT32 i4UpperBound_Shade;
      MINT32 i4LowerBound_Shade;
      // Daylight fluorescent light area
      MINT32 i4RightBound_DaylightFluorescent;
      MINT32 i4LeftBound_DaylightFluorescent;
      MINT32 i4UpperBound_DaylightFluorescent;
      MINT32 i4LowerBound_DaylightFluorescent;
  } AWB_DEBUG_DATA_T; 
"""


def awb_data_debug_old(awb_debug_data, dict_info, exif_name):
    dict_awb_debug = {}
    dict_awb_debug["size"] = awb_debug_data[0]
    dict_awb_debug["is_awb_auto_mode"] = awb_debug_data[1]  # 1:auto mode
    dict_awb_debug["is_strobe_fired"] = awb_debug_data[2]  # 0:strobe is not fired
    dict_awb_debug["parent_blk_num_x"] = awb_debug_data[3]
    dict_awb_debug["parent_blk_num_y"] = awb_debug_data[4]
    dict_awb_debug["sensor_width"] = awb_debug_data[5]
    dict_awb_debug["sensor_height"] = awb_debug_data[6]
    dict_awb_debug["offset_h"] = awb_debug_data[7]
    dict_awb_debug["offset_v"] = awb_debug_data[8]
    dict_awb_debug["parent_blk_width"] = awb_debug_data[9]
    dict_awb_debug["parent_blk_height"] = awb_debug_data[10]
    pb_num_size = (dict_awb_debug["parent_blk_num_x"] + 1) ** 2
    parent_blk_num = dict_awb_debug["parent_blk_num_y"] * dict_awb_debug["parent_blk_num_x"]
    sum_r_data = np.zeros(pb_num_size).astype("uint32")
    sum_g_data = np.zeros(pb_num_size).astype("uint32")
    sum_b_data = np.zeros(pb_num_size).astype("uint32")
    sum_rgblight = np.zeros(shape=(dict_awb_debug["parent_blk_num_y"], dict_awb_debug["parent_blk_num_x"], 4)).astype("uint32")
    sum_r_data = awb_debug_data[11:11 + pb_num_size]
    sum_r_data.shape = [dict_awb_debug["parent_blk_num_x"] + 1, dict_awb_debug["parent_blk_num_x"] + 1]
    sum_r = sum_r_data[0:dict_awb_debug["parent_blk_num_y"], 0:dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_r"] = sum_r
    sum_g_data = awb_debug_data[11 + pb_num_size: 11 + pb_num_size * 2]
    sum_g_data.shape = [dict_awb_debug["parent_blk_num_x"] + 1, dict_awb_debug["parent_blk_num_x"] + 1]
    sum_g = sum_g_data[0:dict_awb_debug["parent_blk_num_y"], 0:dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_g"] = sum_g
    sum_b_data = awb_debug_data[11 + pb_num_size * 2: 11 + pb_num_size * 3]
    sum_b_data.shape = [dict_awb_debug["parent_blk_num_x"] + 1, dict_awb_debug["parent_blk_num_x"] + 1]
    sum_b = sum_b_data[0:dict_awb_debug["parent_blk_num_y"], 0:dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["sum_b"] = sum_b_data
    sum_rgblight[:, :, 0] = sum_r
    sum_rgblight[:, :, 1] = sum_g
    sum_rgblight[:, :, 2] = sum_b
    obj = Process(target=show_awb_debug_data,
                  args=(sum_rgblight[:, :, 0:3], dict_awb_debug["parent_blk_num_x"], dict_awb_debug[
                      "parent_blk_num_y"], 12))
    obj.start()
    child_blk_num = np.zeros(pb_num_size).astype("uint32")
    child_blk_num = awb_debug_data[11 + pb_num_size * 3: 11 + pb_num_size * 4]
    child_blk_num.shape = [dict_awb_debug["parent_blk_num_x"] + 1, dict_awb_debug["parent_blk_num_x"] + 1]
    child_blk_num = child_blk_num[0:dict_awb_debug["parent_blk_num_y"], 0:dict_awb_debug["parent_blk_num_x"]]
    dict_awb_debug["child_blk_num"] = child_blk_num
    light = np.zeros(pb_num_size).astype("uint32")
    light = awb_debug_data[11 + pb_num_size * 4: 11 + pb_num_size * 5]
    light.shape = [dict_awb_debug["parent_blk_num_x"] + 1, dict_awb_debug["parent_blk_num_x"] + 1]
    light = light[0:dict_awb_debug["parent_blk_num_y"], 0:dict_awb_debug["parent_blk_num_x"]]
    sum_rgblight[:, :, 3] = light
    dict_awb_debug["sum_rgblight"] = sum_rgblight
    dict_awb_debug["light"] = light

    dict_awb_debug["central_x"] = awb_debug_data[11 + pb_num_size * 5]
    dict_awb_debug["central_y"] = awb_debug_data[11 + pb_num_size * 5 + 1]
    dict_awb_debug["cos"] = awb_debug_data[11 + pb_num_size * 5 + 2]
    dict_awb_debug["sin"] = awb_debug_data[11 + pb_num_size * 5 + 3]
    dict_awb_debug["right_bound_strobe"] = awb_debug_data[11 + pb_num_size * 5 + 4]
    dict_awb_debug["left_bound_strobe"] = awb_debug_data[11 + pb_num_size * 5 + 5]
    dict_awb_debug["upper_bound_strobe"] = awb_debug_data[11 + pb_num_size * 5 + 6]
    dict_awb_debug["lower_bound_strobe"] = awb_debug_data[11 + pb_num_size * 5 + 7]
    dict_awb_debug["right_bound_tungsten"] = awb_debug_data[11 + pb_num_size * 5 + 8]
    dict_awb_debug["left_bound_tungsten"] = awb_debug_data[11 + pb_num_size * 5 + 9]
    dict_awb_debug["upper_bound_tungsten"] = awb_debug_data[11 + pb_num_size * 5 + 10]
    dict_awb_debug["lower_bound_tungsten"] = awb_debug_data[11 + pb_num_size * 5 + 11]
    dict_awb_debug["right_bound_warmfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 12]
    dict_awb_debug["left_bound_warmfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 13]
    dict_awb_debug["upper_bound_warmfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 14]
    dict_awb_debug["lower_bound_warmfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 15]
    dict_awb_debug["right_bound_fluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 16]
    dict_awb_debug["left_bound_fluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 17]
    dict_awb_debug["upper_bound_fluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 18]
    dict_awb_debug["lower_bound_fluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 19]
    dict_awb_debug["right_bound_cwf"] = awb_debug_data[11 + pb_num_size * 5 + 20]
    dict_awb_debug["left_bound_cwf"] = awb_debug_data[11 + pb_num_size * 5 + 21]
    dict_awb_debug["upper_bound_cwf"] = awb_debug_data[11 + pb_num_size * 5 + 22]
    dict_awb_debug["lower_bound_cwf"] = awb_debug_data[11 + pb_num_size * 5 + 23]
    dict_awb_debug["right_bound_daylight"] = awb_debug_data[11 + pb_num_size * 5 + 24]
    dict_awb_debug["left_bound_daylight"] = awb_debug_data[11 + pb_num_size * 5 + 25]
    dict_awb_debug["upper_bound_daylight"] = awb_debug_data[11 + pb_num_size * 5 + 26]
    dict_awb_debug["lower_bound_daylight"] = awb_debug_data[11 + pb_num_size * 5 + 27]
    dict_awb_debug["right_bound_shade"] = awb_debug_data[11 + pb_num_size * 5 + 28]
    dict_awb_debug["left_bound_shade"] = awb_debug_data[11 + pb_num_size * 5 + 29]
    dict_awb_debug["upper_bound_shade"] = awb_debug_data[11 + pb_num_size * 5 + 30]
    dict_awb_debug["lower_bound_shade"] = awb_debug_data[11 + pb_num_size * 5 + 31]
    dict_awb_debug["right_bound_daylightfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 32]
    dict_awb_debug["left_bound_daylightfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 33]
    dict_awb_debug["upper_bound_daylightfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 34]
    dict_awb_debug["lower_bound_daylightfluorescent"] = awb_debug_data[11 + pb_num_size * 5 + 35]

    return dict_awb_debug


# 显示AWB debug data
def show_awb_debug_data(data, x, y, bits):
    sum_rgb_plt = data / (2 ** bits)
    sum_rgb_plt = sum_rgb_plt.clip(0, 1)
    plt.figure(num='debug_rgb', figsize=(x / 10, y / 10))
    plt.imshow(sum_rgb_plt, interpolation='bicubic', vmax=1.0)
    plt.xticks([]), plt.yticks([])
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.ion()
    plt.pause(20)
    # plt.show()
    plt.close()


def import_reg_data(debug_file_path, table_size):
    reg_tag = np.zeros(shape=(table_size, 3, 33), dtype=int).astype("U750")
    flag_x = 0
    flag_y = 0
    flag_z = 1
    with open(debug_file_path, "r") as debug_file:
        for line in debug_file:
            line = line.replace(",", "\n")
            data_all = line.split("\n")
            data_all = data_all[0].split("    ")
            # print(data_all)
            if data_all[0] != "":
                continue
            if data_all[1] == "]":
                flag_y = flag_y + 1
                flag_z = 1
                continue
            if data_all[1] != "":
                data = data_all[1].split('"')
                flag = int(data[1])
                continue
            if data_all[2] == "[" or data_all[2] == "]":
                continue
            if data_all[2] != "":
                data = data_all[2].split('"')
                for j in range(flag_y, flag):
                    if flag != flag_y:
                        reg_tag[flag_y, flag_x, 0] = str(flag_y)+"_no_exist"
                        flag_y = flag_y + 1
                if data[0] == "":
                    reg_tag[flag_y, flag_x, 0] = data[1]
                else:
                    reg_tag[flag_y, flag_x, 0] = data[0]
                flag_x = flag_x + 1
                if flag_x == 2:
                    flag_x = 0
                continue
            if data_all[3] == "[" or data_all[3] == "]":
                continue
            if data_all[4] != "":
                data = data_all[4].split('"')
                if data[0] == "":
                    reg_tag[flag_y, flag_x, flag_z] = data[1]
                else:
                    reg_tag[flag_y, flag_x, flag_z] = data[0]
                flag_x = flag_x + 1
                if flag_x == 3:
                    flag_x = 0
                    flag_z = flag_z + 1
                continue
        return reg_tag, flag_y


def import_debug_data(debug_file_path):
    tag_data = []
    with open(debug_file_path, "r") as debug_file:
        for line in debug_file:
            line = line.lstrip()
            # print(line)
            if "typedef" in line:
                continue
            elif "enum" in line:
                continue
            elif "{" in line or "}" in line:
                continue
            elif line == "\n":
                continue
            elif line.startswith("//"):
                continue
            elif "AE_TAG_MAX\n" in line:
                continue
            elif line == "":
                continue
            else:
                data_all = line.split(",")
                data = data_all[0].split(" ")
                data = data[0].split("\n")
                data = data[0].split("=")
                tag_data.append(data[0])
    # print(tag_data)
    size = len(tag_data)
    # print(size)
    return tag_data


if __name__ == "__main__":
    # tuning_file_path = "011928646-0932-0932-main3-MFNR_Single.tuning"
    # ae_debug_file_path = "AE_5_7_14.h"
    # ae_debug(ae_debug_file_path, tuning_file_path)
    load_jpg_tuning()
