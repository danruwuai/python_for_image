import numpy as np
import os

AAA_debug = [0, 0, 0xFF, 0xE6]
ISP_debug = [0xFF, 0xE7]
# DEBUG_EXIF_KEYID_AAA = 0xF0F1F200
# DEBUG_EXIF_KEYID_ISP = 0xF4F5F6F7
# DEBUG_PARSER_VERSION = 5
# AAA_DEBUG_KEYID = (DEBUG_EXIF_KEYID_AAA | DEBUG_PARSER_VERSION)
# AAA_Modulecount = [5, 0, 5, 0]


def import_exif_tuning(tuning_file_path):
    dict_aaa = {}
    dict_isp = {}
    tuning_size = os.path.getsize(tuning_file_path)
    print("tuning_size", tuning_size)
    tuning_file = np.fromfile(tuning_file_path, count=tuning_size, dtype="uint8")
    AAA_flag = False
    ISP_flag = False
    for i in range(0, tuning_size):
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
        dict_aaa["aaa_debug_keyid"] = (int(aaa_data[3]) << 24) + (int(aaa_data[2]) << 16) + (int(aaa_data[1]) << 8) + (int(aaa_data[0]) << 0)
        print("AAA_DEBUG_KEYID,", '%#x' %dict_aaa["aaa_debug_keyid"])
        dict_aaa["aaa_version"] = int(aaa_data[0])
        dict_aaa["aaa_modulecount"] = (int(aaa_data[7]) << 24) + (int(aaa_data[6]) << 16) + (int(aaa_data[5]) << 8) + (int(aaa_data[4]) << 0)
        print("AAA_DEBUG_MODULE,", '%#x' %dict_aaa["aaa_modulecount"])
        dict_aaa["ae_debug_info_offset"] = (int(aaa_data[11]) << 24) + (int(aaa_data[10]) << 16) + (int(aaa_data[9]) << 8) + (
                    int(aaa_data[8]) << 0)
        dict_aaa["af_debug_info_offset"] = (int(aaa_data[15]) << 24) + (int(aaa_data[14]) << 16) + (int(aaa_data[13]) << 8) + (
                    int(aaa_data[12]) << 0)
        dict_aaa["flash_debug_info_offset"] = (int(aaa_data[19]) << 24) + (int(aaa_data[18]) << 16) + (int(aaa_data[17]) << 8) + (
                    int(aaa_data[16]) << 0)
        dict_aaa["flicker_debug_info_offset"] = (int(aaa_data[23]) << 24) + (int(aaa_data[22]) << 16) + (int(aaa_data[21]) << 8) + (
                    int(aaa_data[20]) << 0)
        dict_aaa["shading_debug_info_offset"] = (int(aaa_data[27]) << 24) + (int(aaa_data[26]) << 16) + (int(aaa_data[25]) << 8) + (
                    int(aaa_data[24]) << 0)
        dict_aaa["common_size"] = (int(aaa_data[31]) << 24) + (int(aaa_data[30]) << 16) + (int(aaa_data[29]) << 8) + (
                    int(aaa_data[28]) << 0)
        common_data = aaa_data[32:32+dict_aaa["common_size"] - 4]
        dict_aaa["ae_checksum"] = (int(common_data[3]) << 24) + (int(common_data[2]) << 16) + (int(common_data[1]) << 8) + (int(common_data[0]) << 0)
        dict_aaa["ae_ver"] = (int(common_data[5]) << 8) + (int(common_data[4]) << 0)
        dict_aaa["ae_sub"] = (int(common_data[7]) << 8) + (int(common_data[6]) << 0)
        dict_aaa["af_checksum"] = (int(common_data[3+32]) << 24) + (int(common_data[2+32]) << 16) + (int(common_data[1+32]) << 8) + (int(common_data[0+32]) << 0)
        dict_aaa["af_ver"] = (int(common_data[5+32]) << 8) + (int(common_data[4+32]) << 0)
        dict_aaa["af_sub"] = (int(common_data[7+32]) << 8) + (int(common_data[6+32]) << 0)
        dict_aaa["flash_checksum"] = (int(common_data[3+32*2]) << 24) + (int(common_data[2+32*2]) << 16) + (int(common_data[1+32*2]) << 8) + (int(common_data[0+32*2]) << 0)
        dict_aaa["flash_ver"] = (int(common_data[5+32*2]) << 8) + (int(common_data[4+32*2]) << 0)
        dict_aaa["flash_sub"] = (int(common_data[7+32*2]) << 8) + (int(common_data[6+32*2]) << 0)
        dict_aaa["flicker_checksum"] = (int(common_data[3+32*3]) << 24) + (int(common_data[2+32*3]) << 16) + (int(common_data[1+32*3]) << 8) + (int(common_data[0+32*3]) << 0)
        dict_aaa["flicker_ver"] = (int(common_data[5+32*3]) << 8) + (int(common_data[4+32*3]) << 0)
        dict_aaa["flicker_sub"] = (int(common_data[7+32*3]) << 8) + (int(common_data[6+32*3]) << 0)
        dict_aaa["shading_checksum"] = (int(common_data[3+32*4]) << 24) + (int(common_data[2+32*4]) << 16) + (int(common_data[1+32*4]) << 8) + (int(common_data[0+32*4]) << 0)
        dict_aaa["shading_ver"] = (int(common_data[5+32*4]) << 8) + (int(common_data[4+32*4]) << 0)
        dict_aaa["shading_sub"] = (int(common_data[7+32*4]) << 8) + (int(common_data[6+32*4]) << 0)
        ae_tuning_data = aaa_data[dict_aaa["ae_debug_info_offset"]:dict_aaa["af_debug_info_offset"]]
        ae_tuning_size = dict_aaa["af_debug_info_offset"] - dict_aaa["ae_debug_info_offset"]
        ae_tuning_data = ae_tuning_data.astype("int32")
        ae_value_data = (ae_tuning_data[4:ae_tuning_size:8]) + np.left_shift(ae_tuning_data[5:ae_tuning_size:8], 8) +\
                        np.left_shift(ae_tuning_data[6:ae_tuning_size:8], 16) + np.left_shift(ae_tuning_data[7:ae_tuning_size:8], 24)
        print(ae_value_data)
        size = len(ae_value_data)
        print(size)
        return ae_value_data



def ae_debug(ae_debug_file_path, tuning_file_path):
    ae_tag_data = import_debug_ae(ae_debug_file_path)
    ae_value_data = import_exif_tuning(tuning_file_path)
    ae_size = len(ae_tag_data)
    ae_tag = np.array(ae_tag_data)
    ae_value_data = ae_value_data[0:ae_size]
    dict_ae = dict(zip(ae_tag, ae_value_data))
    print(dict_ae)
    save_ae_exif(dict_ae)
    return dict_ae

def save_ae_exif(dict_ae):
    with open("ae.txt", "w") as ae_file:
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
        for key in dict_ae.keys():
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

        """
        ae_file.write('%3d  %3d  %3d  %3d  %3d  \n' % (dict_ae["AE_TAG_STAT_WIN00"], dict_ae["AE_TAG_STAT_WIN01"],
                                                       dict_ae["AE_TAG_STAT_WIN02"],dict_ae["AE_TAG_STAT_WIN03"],
                                                       dict_ae["AE_TAG_STAT_WIN04"]))
        ae_file.write('\n')
        ae_file.write('%3d  %3d  %3d  %3d  %3d  \n' % (dict_ae["AE_TAG_STAT_WIN10"], dict_ae["AE_TAG_STAT_WIN11"],
                                                       dict_ae["AE_TAG_STAT_WIN12"], dict_ae["AE_TAG_STAT_WIN13"],
                                                       dict_ae["AE_TAG_STAT_WIN14"]))
        ae_file.write('\n')
        ae_file.write('%3d  %3d  %3d  %3d  %3d  \n' % (dict_ae["AE_TAG_STAT_WIN20"], dict_ae["AE_TAG_STAT_WIN21"],
                                                       dict_ae["AE_TAG_STAT_WIN22"], dict_ae["AE_TAG_STAT_WIN23"],
                                                       dict_ae["AE_TAG_STAT_WIN24"]))
        ae_file.write('\n')
        ae_file.write('%3d  %3d  %3d  %3d  %3d  \n' % (dict_ae["AE_TAG_STAT_WIN30"], dict_ae["AE_TAG_STAT_WIN31"],
                                                       dict_ae["AE_TAG_STAT_WIN32"], dict_ae["AE_TAG_STAT_WIN33"],
                                                       dict_ae["AE_TAG_STAT_WIN34"]))
        ae_file.write('\n')
        ae_file.write('%3d  %3d  %3d  %3d  %3d  \n' % (dict_ae["AE_TAG_STAT_WIN40"], dict_ae["AE_TAG_STAT_WIN41"],
                                                       dict_ae["AE_TAG_STAT_WIN42"], dict_ae["AE_TAG_STAT_WIN43"],
                                                       dict_ae["AE_TAG_STAT_WIN44"]))
        ae_file.write('\n')
        """
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


def import_debug_ae(ae_debug_file_path):
    ae_tag_data = []
    with open(ae_debug_file_path, "r") as ae_file:
        for line in ae_file:
            if "typedef" in line:
                continue
            elif "{" in line or "}" in line:
                continue
            elif "\n" == line:
                continue
            elif line.startswith("//"):
                continue
            elif "AE_TAG_MAX\n" in line:
                continue
            else:
                data_all = line.split(",")
                data = data_all[0].split(" ")
                data = data[0].split("\n")
                ae_tag_data.append(data[0])
    print(ae_tag_data)
    size = len(ae_tag_data)
    print(size)
    return ae_tag_data



if __name__ == "__main__":
    tuning_file_path = "011928646-0932-0932-main3-MFNR_Single.tuning"
    ae_debug_file_path = "AE_5_7_14.h"
    ae_debug(ae_debug_file_path, tuning_file_path)