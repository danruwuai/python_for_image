import numpy as np
import os
import exif_parser

def get_awb_file(dir_path, jpg_mask):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # file_list.extend(os.path.join(root, file) for file in files if file.endswith("raw_word"))
        # 获取文件名
        for file in files:
            if ((file.endswith("jpg") or file.endswith("tuning") )and os.path.isfile(file)) and file[:19] == jpg_mask:
                return file, True

    return False, False


def get_awb(jpg_mask):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下对应sdblk文件
    awb_file, awb_flag = get_awb_file(current_working_dir, jpg_mask)

    if not awb_flag:
            return False, awb_flag

    dict_awb, dict_isp = exif_parser.load_jpg_data(awb_file)
    print("AWB GAIN is " , dict_awb["AWB_TAG_GAIN_R"], dict_awb["AWB_TAG_GAIN_G"], dict_awb["AWB_TAG_GAIN_B"])
    return dict_awb, dict_isp, awb_flag


def do_awb(image, dict_awb):
    image[:, :, 0] = image[:, :, 0] * dict_awb["AWB_TAG_GAIN_R"] / 512
    image[:, :, 1] = image[:, :, 1] * dict_awb["AWB_TAG_GAIN_G"] / 512
    image[:, :, 2] = image[:, :, 2] * dict_awb["AWB_TAG_GAIN_B"] / 512
    
    image = image.astype(np.uint16)
    return image


def do_ccm(image, dict_isp):
    ccm = np.zeros([3,3], dtype= int)
    ccm[0,0] = dict_isp["SW_CCM_P1_CNV_00"]
    ccm[0,1] = dict_isp["SW_CCM_P1_CNV_01"]
    ccm[0,2] = dict_isp["SW_CCM_P1_CNV_02"]
    ccm[1,0] = dict_isp["SW_CCM_P1_CNV_10"]
    ccm[1,1] = dict_isp["SW_CCM_P1_CNV_11"]
    ccm[1,2] = dict_isp["SW_CCM_P1_CNV_12"]
    ccm[2,0] = dict_isp["SW_CCM_P1_CNV_20"]
    ccm[2,1] = dict_isp["SW_CCM_P1_CNV_21"]
    ccm[2,2] = dict_isp["SW_CCM_P1_CNV_22"]
    print("CCM is \nCNV_00: {:>8d} CNV_01: {:>8d} CNV_02: {:>8d}\nCNV_10: {:>8d} CNV_11: {:>8d} CNV_12: {:>8d}\nCNV_20: {:>8d} CNV_21: {:>8d} CNV_22: {:>8d}"
          .format(ccm[0,0],ccm[0,1],ccm[0,2],ccm[1,0],ccm[1,1],ccm[1,2],ccm[2,0],ccm[2,1],ccm[2,2]))
    
    output = np.empty(np.shape(image), dtype=np.float32)
    output[:, :, 0] = ccm[0,0] / 512 * image[:, :, 0] + ccm[0,1] / 512 * image[:, :, 1] + ccm[0,2] / 512 * image[:, :, 2]
    output[:, :, 1] = ccm[1,0] / 512 * image[:, :, 0] + ccm[1,1] / 512 * image[:, :, 1] + ccm[1,2] / 512 * image[:, :, 2]
    output[:, :, 2] = ccm[2,0] / 512 * image[:, :, 0] + ccm[2,1] / 512 * image[:, :, 1] + ccm[2,2] / 512 * image[:, :, 2]

    output[output<0] = 0
    output = output.astype(np.uint16)
    return output


if __name__ == "__main__":
    jpg_mask = "044829775-0074-0079"
    get_awb(jpg_mask)