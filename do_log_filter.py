import os, sys
from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
from multiprocessing import Process
import re, copy


# 获取当前地址里log名称
def get_main_log_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # 获取文件名,包含main_log文件或者结尾为log的文件，或txt结尾包含log的文件。
        file_list.extend(os.path.join("", file) for file in files if ((file.startswith(
            "main_log_") or file.endswith("log") or (file.endswith("txt") and 'log' in file)) and os.path.isfile(file)))

    return file_list


# 获取config_dat数据
def get_conf_dat(config_data):
    dict_config = {}
    filter_num = []
    filter_count_start = []
    filter_count_end = []
    filter_count_remove = []
    filter_x_start = []
    filter_x_end = []
    filter_x_name = []
    filter_x_remove = []
    filter_y_start = []
    filter_y_end = []
    filter_y_name = []
    filter_y_remove = []
    filter_annotate_start = []
    filter_annotate_end = []
    filter_annotate_remove = []
    filter_color = []
    filter_name = []
    filter_y_threshold = []
    filter_x_mark = []
    config_path = "config.dat"
    # 指定config_path
    if config_data and os.path.isfile(config_data):
        config_path = config_data
    # 确定是否存在config文件
    if not os.path.isfile(config_path):
        return False
    with open(config_path, "r", encoding='utf-8-sig', errors='ignore') as config_file:
        for line in config_file:
            data_all = line.split("//")
            if data_all[0] == "":
                continue
            data = data_all[0].split("    =")
            # 正则表达式添加'\'
            data[1] = data[1].replace("(", "\(")
            data[1] = data[1].replace(")", "\)")
            data[1] = data[1].replace("[", "\[")
            data[1] = data[1].replace("]", "\]")
            data[1] = data[1].replace("{", "\{")
            data[1] = data[1].replace("}", "\}")
            if data[0].split(" ")[0] == "filter_num":
                filter_num.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_count_start":
                filter_count_start.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_count_end":
                filter_count_end.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_count_remove":
                filter_count_remove.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_x_start":
                filter_x_start.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_x_end":
                filter_x_end.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_x_name":
                filter_x_name.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_x_remove":
                filter_x_remove.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_y_start":
                filter_y_start.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_y_end":
                filter_y_end.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_y_name":
                filter_y_name.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_y_remove":
                filter_y_remove.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_annotate_start":
                filter_annotate_start.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_annotate_end":
                filter_annotate_end.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_annotate_remove":
                filter_annotate_remove.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_color":
                filter_color.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_name":
                filter_name.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_y_threshold":
                filter_y_threshold.append(data[1].split("\n")[0])
            elif data[0].split(" ")[0] == "filter_x_mark":
                filter_x_mark.append(data[1].split("\n")[0])
    dict_config["filter_num"] = filter_num
    dict_config["filter_count_start"] = filter_count_start
    dict_config["filter_count_end"] = filter_count_end
    dict_config["filter_count_remove"] = filter_count_remove
    dict_config["filter_x_start"] = filter_x_start
    dict_config["filter_x_end"] = filter_x_end
    dict_config["filter_x_name"] = filter_x_name
    dict_config["filter_x_remove"] = filter_x_remove
    dict_config["filter_y_start"] = filter_y_start
    dict_config["filter_y_end"] = filter_y_end
    dict_config["filter_y_name"] = filter_y_name
    dict_config["filter_y_remove"] = filter_y_remove
    dict_config["filter_annotate_start"] = filter_annotate_start
    dict_config["filter_annotate_end"] = filter_annotate_end
    dict_config["filter_annotate_remove"] = filter_annotate_remove
    dict_config["filter_color"] = filter_color
    dict_config["filter_name"] = filter_name
    dict_config["filter_y_threshold"] = filter_y_threshold
    dict_config["filter_x_mark"] = filter_x_mark
    return dict_config


# 处理log数据
def load_log_file(config_data, log_path):
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_log_list = get_main_log_file(current_working_dir)
    dict_config = get_conf_dat(config_data)
    dict_filter = {}
    filter_num = dict_config["filter_num"]
    filter_count_start = dict_config["filter_count_start"]
    filter_count_end = dict_config["filter_count_end"]
    filter_count_remove = dict_config["filter_count_remove"]
    filter_x_start = dict_config["filter_x_start"]
    filter_x_end = dict_config["filter_x_end"]
    filter_x_name = dict_config["filter_x_name"]
    filter_x_remove = dict_config["filter_x_remove"]
    filter_y_start = dict_config["filter_y_start"]
    filter_y_end = dict_config["filter_y_end"]
    filter_y_name = dict_config["filter_y_name"]
    filter_y_remove = dict_config["filter_y_remove"]
    filter_annotate_start = dict_config["filter_annotate_start"]
    filter_annotate_end = dict_config["filter_annotate_end"]
    filter_annotate_remove = dict_config["filter_annotate_remove"]
    filter_color = dict_config["filter_color"]
    filter_name = dict_config["filter_name"]
    filter_y_threshold = dict_config["filter_y_threshold"]
    filter_x_mark = dict_config["filter_x_mark"]
    # print(file_log_list)
    # print(filter_x_start[0])
    # 循环查找raw的文件
    # 使用输入指定的log_path来替换文件夹里找到的log_list
    if log_path != None and os.path.isfile(log_path):
        file_log_list.clear()
        file_log_list.append(log_path)
        
    for file_log in file_log_list:
        file_name = file_log
        for i in range(0,len(filter_num)):
            dict_filter["filter_count_start"] = filter_count_start[i]
            dict_filter["filter_count_end"] = filter_count_end[i]
            dict_filter["filter_count_remove"] = filter_count_remove[i]
            dict_filter["filter_x_start"] = filter_x_start[i]
            dict_filter["filter_x_end"] = filter_x_end[i]
            dict_filter["filter_x_name"] = filter_x_name[i]
            dict_filter["filter_x_remove"] = filter_x_remove[i]
            dict_filter["filter_y_start"] = filter_y_start[i]
            dict_filter["filter_y_end"] = filter_y_end[i]
            dict_filter["filter_y_name"] = filter_y_name[i]
            dict_filter["filter_y_remove"] = filter_y_remove[i]
            dict_filter["filter_annotate_start"] = filter_annotate_start[i]
            dict_filter["filter_annotate_end"] = filter_annotate_end[i]
            dict_filter["filter_annotate_remove"] = filter_annotate_remove[i]
            dict_filter["filter_color"] = filter_color[i]
            dict_filter["filter_name"] = filter_name[i]
            dict_filter["filter_y_threshold"] = filter_y_threshold[i]
            dict_filter["filter_x_mark"] = filter_x_mark[i]
            obj = Process(target=do_log_show, args=(file_log, dict_filter, file_name))
            obj.start()
            # do_log_show(file_log, dict_filter, file_name)


def do_log_show(file_log, dict_filter, file_name):
    dict_x = {}
    dict_y = {}
    dict_annotate = {}
    dict_x_mark = {}
    y_count = {}
    y_num=len(dict_filter["filter_y_start"].split("|"))
    y_num_remove=len(dict_filter["filter_y_remove"].split("|"))
    # print("y_num: %d  y_num_remove: %d"%(y_num, y_num_remove))
    x = []
    y = []
    x_mark = []
    annotate = []
    for i in range(y_num):
        y_count["start" + "_" + str(i)] = dict_filter["filter_y_start"].split("|")[i]
        y_count["end" + "_" + str(i)] = dict_filter["filter_y_end"].split("|")[i]
        y_count["name" + "_" + str(i)] = dict_filter["filter_y_name"].split("|")[i]
        if y_num == y_num_remove:
            y_count["remove" + "_" + str(i)] = dict_filter["filter_y_remove"].split("|")[i]
        elif i < y_num - 1:
            y_count["remove" + "_" + str(i)] = dict_filter["filter_y_remove"].split("|")[i]
        else:
            y_count["remove" + "_" + str(i)] = ""
        # print( y_count["start" + "_" + str(i)],y_count["end" + "_" + str(i)],y_count["name" + "_" + str(i)],y_count["remove" + "_" + str(i)])
        y.append([])
        x.append([])
        annotate.append([])

    count_num = 0
    pre_count = -1
    with open(file_log, "r", encoding='utf-8-sig', errors='ignore') as log_file:
        for line in log_file:
            if re.search(dict_filter["filter_count_start"], line):
                if dict_filter["filter_count_remove"] == "":
                    count = int(re.findall(f'{dict_filter["filter_count_start"]}('
                                            f'.*?){dict_filter["filter_count_end"]}', line)[0])
                    if pre_count < count:
                        pre_count = count
                    else:
                        # 对齐x,y和注释
                        for i in range(y_num):
                            if len(x[i]) == len(y[i]) + 1:
                                if len(x[i]) == len(annotate[i]):
                                    annotate[i].pop()
                                x[i].pop()
                        pre_count = count
                        dict_x[count_num] = copy.deepcopy(x)
                        dict_y[count_num] = copy.deepcopy(y)
                        dict_annotate[count_num] = copy.deepcopy(annotate)
                        dict_x_mark[count_num] = copy.deepcopy(x_mark)
                        count_num = count_num + 1
                        for i in range(y_num):
                            x[i].clear()
                            y[i].clear()
                            annotate[i].clear()
                        x_mark.clear()
                elif re.search(dict_filter["filter_count_remove"], line):
                    pass
                else:
                    count = int(re.findall(f'{dict_filter["filter_count_start"]}('
                                            f'.*?){dict_filter["filter_count_end"]}', line)[0])
                    if pre_count < count:
                        pre_count = count
                    else:
                        for i in range(y_num):
                            if len(x[i]) == len(y[i]) + 1:
                                if len(x[i]) == len(annotate[i]):
                                    annotate[i].pop()
                                x[i].pop()
                        pre_count = count
                        dict_x[count_num] = copy.deepcopy(x)
                        dict_y[count_num] = copy.deepcopy(y)
                        dict_annotate[count_num] = copy.deepcopy(annotate)
                        dict_x_mark[count_num] = copy.deepcopy(x_mark)
                        count_num = count_num + 1
                        for i in range(y_num):
                            x[i].clear()
                            y[i].clear()
                            annotate[i].clear()
                        x_mark.clear()
            if re.search(dict_filter["filter_x_start"], line):
                if dict_filter["filter_x_remove"] == "":
                    x_data = re.findall(f'{dict_filter["filter_x_start"]}('
                                            f'.*?){dict_filter["filter_x_end"]}', line)[0]
                    for i in range(y_num):
                        if len(x[i]) == len(y[i]):
                            x[i].append(x_data)
                            if len(x[i]) != len(annotate[i]) + 1:
                                annotate[i].append(np.nan)
                        else:
                            if len(x[i]) == len(annotate[i]):
                                annotate[i].pop()
                            x[i].pop()
                            x[i].append(x_data)
                elif re.search(dict_filter["filter_x_remove"], line):
                    pass
                else:
                    x_data = re.findall(f'{dict_filter["filter_x_start"]}(.*?){dict_filter["filter_x_end"]}', line)[0]
                    for i in range(y_num):
                        if len(x[i]) == len(y[i]):
                            x[i].append(x_data)
                            if len(x[i]) != len(annotate[i]) + 1:
                                annotate[i].append(np.nan)
                        else:
                            if len(x[i]) == len(annotate[i]):
                                annotate[i].pop()
                            x[i].pop()
                            x[i].append(x_data)

            for i in range(y_num):
                if re.search(y_count["start" + "_" + str(i)], line):
                    if y_count["remove" + "_" + str(i)] == "":
                        if len(x[i]) == len(y[i]) + 1:
                            y[i].append(re.findall(f'{y_count["start" + "_" + str(i)]}('
                                                f'.*?){y_count["end" + "_" + str(i)]}', line)[0])
                    elif re.search(y_count["remove" + "_" + str(i)], line):
                        pass
                    elif len(x[i]) == len(y[i]) + 1:
                        y[i].append(re.findall(f'{y_count["start" + "_" + str(i)]}(.*?){y_count["end" + "_" + str(i)]}', line)[0])

            if re.search(dict_filter["filter_annotate_start"], line):
                if dict_filter["filter_annotate_remove"] == "":
                    for i in range(y_num):
                        if len(x[i]) == len(annotate[i]) + 1:
                            annotate[i].append(re.findall(
                                f'{dict_filter["filter_annotate_start"]}('
                                f'.*?){dict_filter["filter_annotate_end"]}', line)[0])
                elif re.search(dict_filter["filter_annotate_remove"], line):
                    pass
                else:
                    for i in range(y_num):
                        if len(x[i]) == len(annotate[i]) + 1:
                            annotate[i].append(re.findall(
                                f'{dict_filter["filter_annotate_start"]}('
                                f'.*?){dict_filter["filter_annotate_end"]}', line)[0])
                    
            # 查找标记Y的值
            if dict_filter["filter_x_mark"] == "":
                pass
            elif re.search(dict_filter["filter_x_mark"], line):
                if len(x) ==0:
                    pass
                else:
                    x_mark.append(x_data) 
                
        for i in range(y_num):
            if len(x[i]) == len(y[i]) + 1:
                if len(x[i]) == len(annotate[i]):
                    annotate[i].pop()
                x[i].pop()
        dict_x[count_num] = copy.deepcopy(x)
        dict_y[count_num] = copy.deepcopy(y)
        dict_annotate[count_num] = copy.deepcopy(annotate)
        
        for i in range(count_num + 1):
            x = dict_x[i]
            y = dict_y[i]
            annotate = dict_annotate[i]
            try:
                x_mark = dict_x_mark[i]
            except KeyError:
                x_mark = ""
            
            if len(x) != 0:
                obj = Process(target=show_data, args=(x, y, annotate, y_num, x_mark, dict_filter, file_name + '_' + str(i)))
                obj.start()
                # show_data(x, y, annotate, y_num, x_mark, dict_filter, file_name + '_' + str(i))


def show_data(x, y, annotate, y_num, x_mark, dict_filter, file_name):
    # print(x, y, annotate)
    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))
    y_min = float(y[0][0])
    y_max = float(y[0][0])
    x_min = float(x[0][0])
    x_max = float(x[0][0])
    for i in range(y_num):
        y[i] = np.array(y[i]).astype("float")
        x[i] = np.array(x[i]).astype("float")
        if y_min > y[i].min():
            y_min = y[i].min()
        if y_max < y[i].max():
            y_max = y[i].max()
        if x_min > x[i].min():
            x_min = x[i].min()
        if x_max < x[i].max():
            x_max = x[i].max()
        ax1.plot(x[i], y[i], dict_filter["filter_color"].split("|")[i], label=dict_filter["filter_y_name"].split("|")[i], marker='o')
        ax1.plot(x[i][0], y[i][0], color='r', marker='p')
    # 画X_mark线
    for i in range(len(x_mark)):
        if x_mark != "":
            ax1.axvline(x=float(x_mark[i]), linestyle='--', color='r')
            ax1.annotate(dict_filter["filter_x_mark"], xy=(float(x_mark[i]), y[0].max()), xytext=(float(x_mark[i]), y[0].max() + max((y[0].max() - y[0].min()) * 0.1, 0.02)), arrowprops=dict(arrowstyle="->", color="r"))
    if dict_filter["filter_y_threshold"] != "":
        ax1.axhline(y=float(dict_filter["filter_y_threshold"]), linestyle='--', color='r')
        ax1.annotate(float(dict_filter["filter_y_threshold"]), xy=(x[0].max(), float(dict_filter["filter_y_threshold"])), xytext=(x[0].max(), float(dict_filter["filter_y_threshold"]) + max((y[0].max() - y[0].min()) * 0.1, 0.02)), arrowprops=dict(arrowstyle="->", color="r"))
    # 设置图例
    ax1.legend()
    ax1.set_ylim(y_min - (y_max - y_min) * 0.2, y_max + (y_max-y_min) * 0.2)
    ax1.set_title(file_name + '_' + dict_filter["filter_name"], fontsize=20, fontweight="bold")
    ax1.set_xlabel(dict_filter["filter_x_name"], fontsize=20)
    ax1.set_ylabel(dict_filter["filter_y_name"], fontsize=20)
    ax1.set_xlim(x_min - (x_max - x_min) * 0.05, x_max + (x_max - x_min) * 0.05)

    
    ax1.grid()
    # ax1.arrow(x[0] - 1, y[0] - 1, x[1] - x[0] - 1, y[1] - y[0] - 1, ec ='green')
    """
    # 显示箭头方向
    if x[0] < x[1]:
        ax1.annotate("left", xy=(x.max(), y.max() + max((y.max()-y.min())* 0.05, 0.02)), xytext=(x.max() - (x.max()-x.min())* 0.05, y.max() + max((y.max()-y.min())* 0.05, 0.02)), arrowprops=dict(arrowstyle="->", color="r"))
    else:
        ax1.annotate("right", xy=(x.max() - (x.max()-x.min())* 0.05, y.max() + max((y.max()-y.min())* 0.05, 0.02)), xytext=(x.max(), y.max() + max((y.max()-y.min())* 0.05, 0.02)),  arrowprops=dict(arrowstyle="->", color="r"))
    """

    # 取消坐标轴科学计数法表示
    ax1.get_yaxis().get_major_formatter().set_scientific(False)
    annotate_pre = annotate[0]
    for j in range(y_num):
        for i in range(len(x[j])):
            if str(annotate[j][i]) == str(np.nan):
                continue
            elif i == 0:
                    ax1.annotate(annotate[j][i], xy=(x[j][i], y[j][i]), xytext=(0, 10), textcoords='offset points', color='black')
            elif annotate[j][i] == annotate_pre:
                continue
            else:
                ax1.annotate(annotate[j][i], xy=(x[j][i], y[j][i]), xytext=(0, 10), textcoords='offset points', color='black')
                annotate_pre = annotate[j][i]


    def onselect(xmin, xmax):
        ax2.cla()
        None_flag = 0
        Pre_None_flag = 0
        region_y = []
        print(xmin,xmax)
        for i in range(y_num): 
            flag_bound = False
            # 获取x元素大小排序后的对应的index索引
            a_sort = np.argsort(x[i])
            print(x[i],a_sort)
            ind_min, ind_max = np.searchsorted(x[i], (xmin, xmax), sorter=a_sort)
            if ind_max > len(x[i]) - 1:
                ind_max = len(x[i]) -1
                flag_bound = True
            print(ind_min,ind_max,len(x[i]),'****')
            indmin = a_sort[ind_min]
            indmax = a_sort[ind_max]

            print(indmin,indmax)
            if indmin == indmax:
                region_y.append(np.nan)
                None_flag = None_flag + 1
                continue
            else:
                Pre_None_flag = Pre_None_flag + 1
                if indmin > indmax:
                    data_ind = copy.deepcopy(indmin)
                    if indmax == 0:
                        indmin = copy.deepcopy(indmax)
                    elif flag_bound:
                        indmin = copy.deepcopy(indmax)
                    else:
                        indmin = copy.deepcopy(indmax) + 1
                    indmax = copy.deepcopy(data_ind) + 1
                elif flag_bound:
                    indmax = indmax + 1
                else:
                    indmax = indmax - 1
                print(indmin,indmax,"##########")
            if Pre_None_flag == 1:
                region_y_min = y[Pre_None_flag + None_flag - 1][indmin]
                region_y_max = y[Pre_None_flag + None_flag - 1][indmin]
                region_x_min = x[Pre_None_flag + None_flag - 1][indmin]
                region_x_max = x[Pre_None_flag + None_flag - 1][indmin]
            indmax = min(len(x[i]), indmax)
            region_x = x[i][indmin:indmax]
            region_y.append(y[i][indmin:indmax])
            if region_y_min > region_y[i].min():
                region_y_min = region_y[i].min()
            if region_y_max < region_y[i].max():
                region_y_max = region_y[i].max()
            if region_x_min > region_x.min():
                region_x_min = region_x.min()
            if region_x_max < region_x.max():
                region_x_max = region_x.max()
            print(region_x_min, region_x_max, region_y_min, region_y_max)
            ax2.plot(region_x, region_y[i], 'o:' + dict_filter["filter_color"].split("|")[i], label=dict_filter["filter_y_name"].split("|")[i])
            # 标记起始位置
            ax2.plot(region_x[0], region_y[i][0], color='r', marker='p')
            #line2.set_data(region_x, region_y[i])

            region_annotate = annotate[i][indmin:indmax]
            region_annotate_pre = region_annotate[i][0]
            print(region_x, region_y, region_annotate, indmin, indmax)
            for j in range(indmax-indmin):
                if str(region_annotate[j]) == str(np.nan):
                    continue
                elif j == 0:
                    ax2.annotate(region_annotate[j], xy=(region_x[j], region_y[i][j]), xytext=(0, 10), textcoords='offset points', color='black')
                    region_annotate_pre = region_annotate[j]
                    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx%d %d %d ", i,region_x[i],region_y[i])
                elif region_annotate[j] == region_annotate_pre:
                    continue
                else:
                    ax2.annotate(region_annotate[j], xy=(region_x[j], region_y[i][j]), xytext=(0, 10), textcoords='offset points', color='black')
                    region_annotate_pre = region_annotate[j]
                    # print("22222222222222222%d", i)
        
        ax2.legend()
        ax2.set_xlim(region_x_min - (region_x_max - region_x_min) * 0.05, region_x_max + (region_x_max - region_x_min) * 0.05)
        ax2.set_ylim(region_y_min - (region_y_max-region_y_min) * 0.2, region_y_max+(region_y_max-region_y_min) * 0.2)
        ax2.set_xlabel(dict_filter["filter_x_name"], fontsize=20)
        ax2.set_ylabel(dict_filter["filter_y_name"], fontsize=20)
        
        
        
        # 画X_mark线
        for i in range(len(x_mark)):
            if indmin <= float(x_mark[i]) <= indmax :
                ax2.axvline(x=float(x_mark[i]), linestyle='--', color='r')
                ax2.annotate(dict_filter["filter_x_mark"], xy=(float(x_mark[i]), region_y[0].max()), xytext=(float(x_mark[i]), region_y[0].max() + max((region_y[0].max() - region_y[0].min()) * 0.1, 0.02)), arrowprops=dict(arrowstyle="->", color="r"))
        if dict_filter["filter_y_threshold"] != "":
            ax2.axhline(y=float(dict_filter["filter_y_threshold"]), linestyle='--', color='r')
            ax2.annotate(float(dict_filter["filter_y_threshold"]), xy=(region_x_max, float(dict_filter["filter_y_threshold"])), xytext=(region_x_max, float(dict_filter["filter_y_threshold"]) + max((region_y[0].max() - region_y[0].min()) * 0.1, 0.02)), arrowprops=dict(arrowstyle="->", color="r"))
        
        # 整数显示横坐标
        x_ticks_num = int(len(region_x) / 10)
        if x_ticks_num == 0:
            ax2.set_xticks(region_x)
        else:
            ax2.set_xticks(region_x[::x_ticks_num])
        # 显示网格
        ax2.grid()
        # ax2.set_xlim(x[indmin], x[indmax], indmax - indmin)
        # 取消坐标轴科学计数法表示
        ax2.get_yaxis().get_major_formatter().set_scientific(False)
        fig.canvas.draw()
    span = SpanSelector(ax1, onselect, 'horizontal', useblit=True, rectprops=dict(
        alpha=0.5, facecolor='tab:blue'))
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=2.0)
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()


if __name__ == "__main__":
    # 添加输入信息
    if len(sys.argv) > 1:
        config_data = sys.argv[1]
        if config_data == "Zhong":
            print("################################################################")
            print("Design by Zhongguojun")
            print("Creation time:2022/09/10")
            print("################################################################")
    else:
        config_data = 0
    if len(sys.argv) > 2:
        log_path = sys.argv[2]
    else:
        log_path = None
    load_log_file(config_data, log_path)
    