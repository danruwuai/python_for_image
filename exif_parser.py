import os
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
        file_list.extend(os.path.join("", file) for file in files if (file.endswith("jpg") or file.endswith("tuning") or file.endswith("ispinfo") and os.path.isfile(file)))

    return file_list


def load_jpg_tuning():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_exif_list = get_jpg_tuning_ispinfo_file(current_working_dir)
    # Exif 地址
    exif = current_working_dir + "/EXIF"
    # print(file_exif_list)
    # 循环查找raw的文件
    for file_exif in file_exif_list:
        print("获取的文件：", file_exif)
        exif_name = file_exif + ".exif"
        dict_data, dict_info = import_exif_tuning(file_exif)
        ae_debug(dict_data["ae_value_data"], dict_info, exif, exif_name)
        if dict_info["aaa_modulecount"] == 0x70005:
            ae_debug_data(dict_data["ae_debug_value_data"], exif_name)
        af_debug(dict_data["af_value_data"], dict_info, exif, exif_name)
        awb_debug(dict_data["awb_value_data"], dict_info, exif, exif_name)
        shading_debug(dict_data["shading_value_data"], dict_info, exif, exif_name)
        flash_debug(dict_data["flash_value_data"], dict_info, exif, exif_name)
        isp_debug(dict_data["isp_value_data"], dict_info, exif, exif_name)
        


def load_jpg_data(file):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    exif = current_working_dir + "/EXIF"
    print("获取的文件：", file)
    exif_name = file + "_awb.exif"
    dict_data, dict_info = import_exif_tuning(file)
        
    dict_awb = awb_debug(dict_data["awb_value_data"], dict_info, exif, exif_name)
    dict_isp = isp_debug(dict_data["isp_value_data"], dict_info, exif, exif_name)
    return dict_awb, dict_isp


def import_exif_tuning(tuning_file_path):
    dict_info = {}
    dict_data = {}

    tuning_size = os.path.getsize(tuning_file_path)
    print("tuning_size", tuning_size)
    tuning_file = np.fromfile(tuning_file_path, count=tuning_size, dtype="uint8")
    AAA_flag = False
    ISP_flag = False
    for i in range(tuning_size):
        if not AAA_flag and tuning_file[i] == AAA_debug[0] and tuning_file[i+1] == \
                AAA_debug[1] and tuning_file[i+2] == AAA_debug[2] and tuning_file[i+3] == AAA_debug[3]:
            AAA_size = (int(tuning_file[i+4]) << 8) + tuning_file[i+5]
            print("AAA_size", AAA_size)
            aaa_data = tuning_file[i+6: i+6+AAA_size-2]
            AAA_flag = True
            if tuning_file[i+6+AAA_size-2] == ISP_debug[0] and tuning_file[i+6+AAA_size-1] == ISP_debug[1]:
                ISP_size = (int(tuning_file[i+6+AAA_size]) << 8) + tuning_file[i+6+AAA_size+1]
                print("ISP_size", ISP_size)
                isp_data = tuning_file[i+6+AAA_size+2:i+6+AAA_size+ISP_size]
                ISP_flag = True
        if not ISP_flag and tuning_file[i] == ISP_debug[0] and tuning_file[i+1] == ISP_debug[1]:
            ISP_size = (int(tuning_file[i + 2]) << 8) + tuning_file[i + 3]
            print("ISP_size", ISP_size)
            isp_data = tuning_file[i + 4:i + 4 + ISP_size -2]
            ISP_flag = True
        if AAA_flag and ISP_flag:
            break
    if not AAA_flag:
        print("not exit AAA_exif")
    else:
        dict_info["aaa_debug_keyid"] = (int(aaa_data[3]) << 24) + (int(aaa_data[2]) << 16) + (int(aaa_data[1]) << 8) + (int(aaa_data[0]) << 0)
        print("AAA_DEBUG_KEYID,", '%#x' %dict_info["aaa_debug_keyid"])
        dict_info["debug_parser_version"] = int(aaa_data[0])
        dict_info["aaa_modulecount"] = (int(aaa_data[7]) << 24) + (int(aaa_data[6]) << 16) + (int(aaa_data[5]) << 8) + (int(aaa_data[4]) << 0)
        print("AAA_DEBUG_MODULE,", '%#x' %dict_info["aaa_modulecount"])
        dict_info["ae_debug_info_offset"] = (int(aaa_data[11]) << 24) + (int(aaa_data[10]) << 16) + (int(aaa_data[9]) << 8) + (
                    int(aaa_data[8]) << 0)
        dict_info["af_debug_info_offset"] = (int(aaa_data[15]) << 24) + (int(aaa_data[14]) << 16) + (int(aaa_data[13]) << 8) + (
                    int(aaa_data[12]) << 0)
        dict_info["flash_debug_info_offset"] = (int(aaa_data[19]) << 24) + (int(aaa_data[18]) << 16) + (int(aaa_data[17]) << 8) + (
                    int(aaa_data[16]) << 0)
        dict_info["flicker_debug_info_offset"] = (int(aaa_data[23]) << 24) + (int(aaa_data[22]) << 16) + (int(aaa_data[21]) << 8) + (
                    int(aaa_data[20]) << 0)
        dict_info["shading_debug_info_offset"] = (int(aaa_data[27]) << 24) + (int(aaa_data[26]) << 16) + (int(aaa_data[25]) << 8) + (
                    int(aaa_data[24]) << 0)
        if dict_info["aaa_modulecount"] == 0x50005:
            dict_info["aaa_common_size"] = (int(aaa_data[31]) << 24) + (int(aaa_data[30]) << 16) + (int(aaa_data[29]) << 8) + (
                    int(aaa_data[28]) << 0)
            aaa_common_data = aaa_data[32:32+dict_info["aaa_common_size"] - 4]
        else:
            dict_info["ae_debug_data_offset"] = (int(aaa_data[31]) << 24) + (int(aaa_data[30]) << 16) + (int(aaa_data[29]) << 8) + (
                    int(aaa_data[28]) << 0)
            dict_info["string_debug_info_offset"] = (int(aaa_data[35]) << 24) + (int(aaa_data[34]) << 16) + (int(aaa_data[33]) << 8) + (
                    int(aaa_data[32]) << 0)
            dict_info["aaa_common_size"] = (int(aaa_data[39]) << 24) + (int(aaa_data[38]) << 16) + (int(aaa_data[37]) << 8) + (
                    int(aaa_data[36]) << 0)
            aaa_common_data = aaa_data[40:40+dict_info["aaa_common_size"] - 4]
        dict_info["ae_checksum"] = (int(aaa_common_data[3]) << 24) + (int(aaa_common_data[2]) << 16) + (int(aaa_common_data[1]) << 8) + (int(aaa_common_data[0]) << 0)
        dict_info["ae_ver"] = (int(aaa_common_data[5]) << 8) + (int(aaa_common_data[4]) << 0)
        dict_info["ae_sub"] = (int(aaa_common_data[7]) << 8) + (int(aaa_common_data[6]) << 0)
        print(dict_info["ae_ver"],dict_info["ae_sub"])
        dict_info["af_checksum"] = (int(aaa_common_data[3+32]) << 24) + (int(aaa_common_data[2+32]) << 16) + (int(aaa_common_data[1+32]) << 8) + (int(aaa_common_data[0+32]) << 0)
        dict_info["af_ver"] = (int(aaa_common_data[5+32]) << 8) + (int(aaa_common_data[4+32]) << 0)
        dict_info["af_sub"] = (int(aaa_common_data[7+32]) << 8) + (int(aaa_common_data[6+32]) << 0)
        dict_info["flash_checksum"] = (int(aaa_common_data[3+32*2]) << 24) + (int(aaa_common_data[2+32*2]) << 16) + (int(aaa_common_data[1+32*2]) << 8) + (int(aaa_common_data[0+32*2]) << 0)
        dict_info["flash_ver"] = (int(aaa_common_data[5+32*2]) << 8) + (int(aaa_common_data[4+32*2]) << 0)
        dict_info["flash_sub"] = (int(aaa_common_data[7+32*2]) << 8) + (int(aaa_common_data[6+32*2]) << 0)
        dict_info["flicker_checksum"] = (int(aaa_common_data[3+32*3]) << 24) + (int(aaa_common_data[2+32*3]) << 16) + (int(aaa_common_data[1+32*3]) << 8) + (int(aaa_common_data[0+32*3]) << 0)
        dict_info["flicker_ver"] = (int(aaa_common_data[5+32*3]) << 8) + (int(aaa_common_data[4+32*3]) << 0)
        dict_info["flicker_sub"] = (int(aaa_common_data[7+32*3]) << 8) + (int(aaa_common_data[6+32*3]) << 0)
        dict_info["shading_checksum"] = (int(aaa_common_data[3+32*4]) << 24) + (int(aaa_common_data[2+32*4]) << 16) + (int(aaa_common_data[1+32*4]) << 8) + (int(aaa_common_data[0+32*4]) << 0)
        dict_info["shading_ver"] = (int(aaa_common_data[5+32*4]) << 8) + (int(aaa_common_data[4+32*4]) << 0)
        dict_info["shading_sub"] = (int(aaa_common_data[7+32*4]) << 8) + (int(aaa_common_data[6+32*4]) << 0)
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
        dict_data["af_value_data"] = cal_aaa_value(af_tuning_data, af_tuning_size)
        dict_data["shading_value_data"] = cal_aaa_value(shading_tuning_data, shading_tuning_size)
        dict_data["flash_value_data"] = cal_aaa_value(flash_tuning_data, flash_tuning_size)
        if dict_info["aaa_modulecount"] == 0x70005:
            dict_data["ae_debug_value_data"] = cal_ae_data_value(ae_debug_data, ae_debug_size)
    if not ISP_flag:
        print("not exit ISP_exif")
    else:
        dict_info["isp_debug_keyid"] = (int(isp_data[3]) << 24) + (int(isp_data[2]) << 16) + (int(isp_data[1]) << 8) + (int(isp_data[0]) << 0)
        print("ISP_DEBUG_KEYID,", '%#x' %dict_info["isp_debug_keyid"])
        dict_info["isp_modulecount"] = (int(isp_data[7]) << 24) + (int(isp_data[6]) << 16) + (int(isp_data[5]) << 8) + (int(isp_data[4]) << 0)
        print("ISP_DEBUG_MODULE,", '%#x' %dict_info["isp_modulecount"])
        dict_info["awb_debug_info_offset"] = (int(isp_data[11]) << 24) + (int(isp_data[10]) << 16) + (int(isp_data[9]) << 8) + (
                    int(isp_data[8]) << 0)
        dict_info["isp_debug_info_offset"] = (int(isp_data[15]) << 24) + (int(isp_data[14]) << 16) + (int(isp_data[13]) << 8) + (
                    int(isp_data[12]) << 0)
        dict_info["awb_debug_data_offset"] = (int(isp_data[19]) << 24) + (int(isp_data[18]) << 16) + (int(isp_data[17]) << 8) + (
                    int(isp_data[16]) << 0)
        dict_info["isp_common_size"] = (int(isp_data[23]) << 24) + (int(isp_data[22]) << 16) + (int(isp_data[21]) << 8) + (
                    int(isp_data[20]) << 0)
        isp_common_data = isp_data[24:24+dict_info["isp_common_size"] - 4]
        dict_info["awb_checksum"] = (int(isp_common_data[3]) << 24) + (int(isp_common_data[2]) << 16) + (int(isp_common_data[1]) << 8) + (int(isp_common_data[0]) << 0)
        dict_info["awb_ver"] = (int(isp_common_data[5]) << 8) + (int(isp_common_data[4]) << 0)
        dict_info["awb_sub"] = (int(isp_common_data[7]) << 8) + (int(isp_common_data[6]) << 0)
        print(dict_info["awb_ver"],dict_info["awb_sub"])
        
        dict_info["isp_checksum"] = (int(isp_common_data[3+32]) << 24) + (int(isp_common_data[2+32]) << 16) + (int(isp_common_data[1+32]) << 8) + (int(isp_common_data[0+32]) << 0)
        dict_info["isp_ver"] = (int(isp_common_data[5+32]) << 8) + (int(isp_common_data[4+32]) << 0)
        dict_info["isp_sub"] = (int(isp_common_data[7+32]) << 8) + (int(isp_common_data[6+32]) << 0)
        print(dict_info["isp_ver"],dict_info["isp_sub"])
        # 获取AWB value的值
        awb_tuning_data = isp_data[dict_info["awb_debug_info_offset"]:dict_info["isp_debug_info_offset"]]
        awb_tuning_size = dict_info["isp_debug_info_offset"] - dict_info["awb_debug_info_offset"]
        awb_tuning_data = awb_tuning_data.astype("int32")
        
        dict_data["awb_value_data"] = cal_isp_value(awb_tuning_data, awb_tuning_size)
        # 获取ISP value的值
        isp_tuning_data = isp_data[dict_info["isp_debug_info_offset"]:dict_info["awb_debug_data_offset"]]
        isp_tuning_size = dict_info["awb_debug_data_offset"] - dict_info["isp_debug_info_offset"]
        isp_tuning_data = isp_tuning_data.astype("int32")
        
        dict_data["isp_value_data"] = cal_isp_value(isp_tuning_data, isp_tuning_size)
    return dict_data, dict_info    


def cal_aaa_value(tuning_data, tuning_size):
    value_data = (tuning_data[4:tuning_size:8]) + np.left_shift(tuning_data[5:tuning_size:8], 8) +\
                    np.left_shift(tuning_data[6:tuning_size:8], 16) + np.left_shift(tuning_data[7:tuning_size:8], 24)
    value_num = tuning_data[:tuning_size:8] + tuning_data[1:tuning_size:8] + tuning_data[2:tuning_size:8] + tuning_data[3:tuning_size:8] + tuning_data[4:tuning_size:8] + tuning_data[5:tuning_size:8] + tuning_data[6:tuning_size:8] + tuning_data[7:tuning_size:8]
    value_data = value_data.astype("int64")
    value_data[value_num == 0] = 0xfffffffff
    # print(value_data)
    size = len(value_data)
    print(size)

    return value_data


def cal_isp_value(tuning_data, tuning_size):
    value_data = (tuning_data[0:tuning_size:4]) + np.left_shift(tuning_data[1:tuning_size:4], 8) +\
                    np.left_shift(tuning_data[2:tuning_size:4], 16) + np.left_shift(tuning_data[3:tuning_size:4], 24)
    return value_data


def cal_ae_data_value(tuning_data, tuning_size):
    value_data = np.zeros((tuning_size-2048)//4 + 2048 //2).astype("uint32")
    value_data[0:1024] = tuning_data[0:2048:2] + np.left_shift(tuning_data[1:2048:2], 8)
    value_data[1024:(tuning_size-2048)//4 + 2048 //2] = (tuning_data[2048:tuning_size:4]) +\
    np.left_shift(tuning_data[2048 + 1:tuning_size:4], 8) + np.left_shift(tuning_data[2048 + 2:tuning_size:4], 16) +\
    np.left_shift(tuning_data[2048 + 3:tuning_size:4], 24)
    
    return value_data



def ae_debug(ae_value_data, dict_info, exif, exif_name):
    ae_version = exif + "/AE/AE_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["ae_ver"], dict_info["ae_sub"])
    # print("ae_version", ae_version)
    ae_tag_data = import_debug_data(ae_version)
    ae_size = len(ae_tag_data)
    ae_tag = np.array(ae_tag_data)
    ae_value_data = ae_value_data[0:ae_size]
    dict_ae = dict(zip(ae_tag, ae_value_data))
    # print(dict_ae)
    save_ae_exif(dict_ae, dict_info, exif_name)
    return dict_ae


def save_ae_exif(dict_ae, dict_info, exif_name):
    with open(exif_name, "w") as ae_file:
        ae_file.write('[AE]\n')
        i = 0
        data_5_5 = np.zeros(5*5).astype("uint32")
        data_15_15_y = np.zeros(15*15).astype("uint32")
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
                    if i > 19 and i < 40:
                        i = 40
                    elif i > 59 and i < 80:
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
        LE_R_16_12[i,0:width_num] = ae_debug_data[i * width_num + 8:i * width_num + 8 + width_num]
        LE_G_16_12[i,0:width_num] = ae_debug_data[256 + i * width_num + 8:256 + i * width_num + 8 + width_num]
        LE_B_16_12[i,0:width_num] = ae_debug_data[512 + i * width_num + 8:512 + i * width_num + 8 + width_num]
        LE_Y_16_12[i,0:width_num] = ae_debug_data[768 + i * width_num + 8:768 + i * width_num + 8 + width_num]
        
    # 读取histogram信息
    LE_RGB_MAX_hist = ae_debug_data[1024 + 4: 1024 + 4 + 256]
    LE_Y_hist = ae_debug_data[1024 + 256 + 4: 1024 + 256 + 4 + 256]
    SE_Y_hist = ae_debug_data[1024 + 256 * 2 + 4: 1024 + 256 * 2 + 4 + 256]
    obj = Process(target=show_ae_data, args=(LE_R_16_12, LE_G_16_12, LE_B_16_12, LE_Y_16_12, LE_RGB_MAX_hist, LE_Y_hist, SE_Y_hist, width_num, height_num))
    obj.start()
    
    with open(exif_name, "a") as ae_file:
        ae_file.write('\n')
        ae_file.write('[AE_Table]\n')
        ae_file.write('<<16_12_LE_Y>>\n')
        
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_Y_16_12[i//width_num, i%width_num]))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')
    
        ae_file.write('<<16_12_LE_R>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_R_16_12[i // width_num,i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')
    
    
        ae_file.write('<<16_12_LE_G>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_G_16_12[i // width_num,i % width_num]).ljust(3))
            if (i + 1) % width_num == 0 and i > 0:
                ae_file.write('\n')
                ae_file.write('\n')
    
        ae_file.write('<<16_12_LE_B>>\n')
        for i in range(data_num):
            ae_file.write(' %3s ' % str(LE_B_16_12[i // width_num,i % width_num]).ljust(3))
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





def show_ae_data(LE_R_16_12, LE_G_16_12, LE_B_16_12, LE_Y_16_12, LE_RGB_MAX_hist, LE_Y_hist, SE_Y_hist, width_num, height_num):
    X = np.arange(0, width_num)
    Y = np.arange(0, height_num)
    print(X,Y)
    X, Y = np.meshgrid(X, Y)
    print(X,Y)
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
    plt.suptitle("Block")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    fig2, ax1 = plt.subplots(3, figsize=(10, 4.5))
    ax1[0].bar(range(len(LE_RGB_MAX_hist)), LE_RGB_MAX_hist, color='gray')
    ax1[0].set_title('LE_RGB_MAX_hist', color='r', loc="left")  # 设置标题
    
    ax1[1].bar(range(len(LE_Y_hist)), LE_Y_hist, color='gray')
    ax1[1].set_title('LE_Y_hist', color='r', loc="left")  # 设置标题
    
    ax1[2].bar(range(len(SE_Y_hist)), SE_Y_hist, color='gray')
    ax1[2].set_title('SE_Y_hist', color='r', loc="left")  # 设置标题
    plt.suptitle("Histogram")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.ion()
    plt.pause(20)
    # plt.show()
    plt.close()


def af_debug(af_value_data, dict_info, exif, exif_name):
    af_version = exif + "/AF/AF_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["af_ver"], dict_info["af_sub"])
    # print("af_version", af_version)
    af_tag_data = import_debug_data(af_version)
    af_size = len(af_tag_data)
    af_tag = np.array(af_tag_data)
    af_value_data = af_value_data[0:af_size]
    dict_af = dict(zip(af_tag, af_value_data))
    # print(dict_af)
    save_af_exif(dict_af, dict_info, exif_name)
    return dict_af


def save_af_exif(dict_af, dict_info, exif_name):
    with open(exif_name, "a") as af_file:
        af_file.write('\n')
        af_file.write('[AF]\n')
        for key in dict_af.keys():
            if dict_af[key] == 0xfffffffff:
                continue
            af_file.write('%56s:%13d | \n' % (key.ljust(56), dict_af[key]))


def awb_debug(awb_value_data, dict_info, exif, exif_name):
    awb_version = exif + "/AWB/AWB_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["awb_ver"], dict_info["awb_sub"])
    # print("awb_version", awb_version)
    awb_tag_data = import_debug_data(awb_version)
    awb_size = len(awb_tag_data)
    awb_tag = np.array(awb_tag_data)
    awb_value_data = awb_value_data[0:awb_size]
    dict_awb = dict(zip(awb_tag, awb_value_data))
    # print(dict_awb)
    save_awb_exif(dict_awb, dict_info, exif_name)
    return dict_awb


def save_awb_exif(dict_awb, dict_info, exif_name):
    with open(exif_name, "a") as awb_file:
        awb_file.write('\n')
        awb_file.write('[AWB]\n')
        for key in dict_awb.keys():
            awb_file.write('%48s:%13d | \n' % (key.ljust(48), dict_awb[key]))


def shading_debug(shading_value_data, dict_info, exif, exif_name):
    shading_version = exif + "/SHADING/SHADING_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["shading_ver"], dict_info["shading_sub"])
    # print("shading_version", shading_version)
    shading_tag_data = import_debug_data(shading_version)
    shading_size = len(shading_tag_data)
    shading_tag = np.array(shading_tag_data)
    shading_value_data = shading_value_data[0:shading_size]
    dict_shading = dict(zip(shading_tag, shading_value_data))
    # print(dict_shading)
    save_shading_exif(dict_shading, dict_info, exif_name)
    return dict_shading


def save_shading_exif(dict_shading, dict_info, exif_name):
    with open(exif_name, "a") as shading_file:
        shading_file.write('\n')
        shading_file.write('[Shading]\n')
        for key in dict_shading.keys():
            if dict_shading[key] == 0xfffffffff:
                continue
            shading_file.write('%32s:%13d | \n' % (key.ljust(32), dict_shading[key]))
        shading_file.write('\n')


def flash_debug(flash_value_data, dict_info, exif, exif_name):
    flash_version = exif + "/STROBE/STROBE_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["flash_ver"], dict_info["flash_sub"])
    # print("flash_version", flash_version)
    flash_tag_data = import_debug_data(flash_version)
    flash_size = len(flash_tag_data)
    flash_tag = np.array(flash_tag_data)
    flash_value_data = flash_value_data[0:flash_size]
    dict_flash = dict(zip(flash_tag, flash_value_data))
    # print(dict_flash)
    save_flash_exif(dict_flash, dict_info, exif_name)
    return dict_flash


def save_flash_exif(dict_flash, dict_info, exif_name):
    with open(exif_name, "a") as flash_file:
        flash_file.write('\n')
        flash_file.write('\n')
        flash_file.write('[Strobe]\n')
        for key in dict_flash.keys():
            if dict_flash[key] == 0xfffffffff:
                continue
            flash_file.write('%28s:%13d | \n' % (key.ljust(28), dict_flash[key]))
        flash_file.write('\n')


def isp_debug(isp_value_data, dict_info, exif, exif_name):
    isp_version = exif + "/ISP/ISP_{}_{}_{}.h".format(dict_info["debug_parser_version"], dict_info["isp_ver"], dict_info["isp_sub"])
    # print("isp_version", isp_version)
    isp_tag_data = import_debug_data(isp_version)
    isp_size = len(isp_tag_data)
    isp_tag = np.array(isp_tag_data)
    isp_value_data = isp_value_data[0:isp_size]
    dict_isp = dict(zip(isp_tag, isp_value_data))
    # print(dict_isp)
    save_isp_exif(dict_isp, dict_info, exif_name)
    return dict_isp


def save_isp_exif(dict_isp, dict_info, exif_name):
    with open(exif_name, "a") as isp_file:
        isp_file.write('\n')
        isp_file.write('\n')
        isp_file.write('[ISP]\n')
        for key in dict_isp.keys():
            isp_file.write('%56s:%13d | \n' % (key.ljust(56), dict_isp[key]))
        isp_file.write('\n')


def import_debug_data(debug_file_path):
    tag_data = []
    with open(debug_file_path, "r") as debug_file:
        for line in debug_file:
            line = line.lstrip()
            print(line)
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
    print(size)
    return tag_data



if __name__ == "__main__":
    #tuning_file_path = "011928646-0932-0932-main3-MFNR_Single.tuning"
    #ae_debug_file_path = "AE_5_7_14.h"
    #ae_debug(ae_debug_file_path, tuning_file_path)
    load_jpg_tuning()