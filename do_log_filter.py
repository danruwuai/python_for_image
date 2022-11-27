import os
from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
from multiprocessing import Process
import re


# 获取当前地址里log名称
def get_main_log_file(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        # 获取完整路径
        # 获取文件名
        file_list.extend(os.path.join("", file) for file in files if (file.startswith(
            "main_log_") and os.path.isfile(file)))

    return file_list


# 获取config_dat数据
def get_conf_dat():
    dict_config = {}
    filter_num = []
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
    if not os.path.isfile("config.dat"):
        return False
    with open("config.dat", "r") as config_file:
        for line in config_file:
            data_all = line.split("//")
            if data_all[0] == "":
                continue
            data = data_all[0].split("    =")
            data[1] = data[1].replace("(", "\(")
            data[1] = data[1].replace(")", "\)")
            data[1] = data[1].replace("[", "\[")
            data[1] = data[1].replace("]", "\]")
            if data[0].split(" ")[0] == "filter_num":
                filter_num.append(data[1].split("\n")[0])
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
    dict_config["filter_num"] = filter_num
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

    return dict_config


# 处理log数据
def load_log_flie():
    # 获取文件所在的路径
    current_working_dir = os.getcwd()
    # 路径下所有文件列表
    file_log_list = get_main_log_file(current_working_dir)
    dict_config = get_conf_dat()
    dict_filter = {}
    filter_num = dict_config["filter_num"]
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

    # print(file_log_list)
    print(filter_x_start[0])
    # 循环查找raw的文件
    for file_log in file_log_list:
        file_name = file_log
        for i in range(0, len(filter_num)):
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
            obj = Process(target=do_log_show, args=(file_log, dict_filter, file_name))
            obj.start()
            # do_log_show(file_log, dict_filter)


def do_log_show(file_log, dict_filter, file_name):
    x = []
    y = []
    annotate = []
    with open(file_log, "r", encoding='utf-8-sig', errors='ignore') as log_file:
        for line in log_file:
            if re.search(dict_filter["filter_x_start"], line):
                if dict_filter["filter_x_remove"] == "":
                    if len(x) == len(y):
                        x.append(re.findall(f'{dict_filter["filter_x_start"]}('
                                            f'.*?){dict_filter["filter_x_end"]}', line)[0])
                        if len(x) != len(annotate) + 1:
                            annotate.append(np.nan)
                    else:
                        if len(x) == len(annotate):
                            annotate.pop()
                        x.pop()
                        x.append(re.findall(f'{dict_filter["filter_x_start"]}('
                                            f'.*?){dict_filter["filter_x_end"]}', line)[0])
                elif re.search(dict_filter["filter_x_remove"], line):
                    pass
                elif len(x) == len(y):
                    x.append(re.findall(f'{dict_filter["filter_x_start"]}(.*?){dict_filter["filter_x_end"]}', line)[0])
                    if len(x) != len(annotate) + 1:
                        annotate.append(np.nan)
                else:
                    if len(x) == len(annotate):
                        annotate.pop()
                    x.pop()
                    x.append(re.findall(f'{dict_filter["filter_x_start"]}(.*?){dict_filter["filter_x_end"]}', line)[0])

            if re.search(dict_filter["filter_y_start"], line):
                if dict_filter["filter_y_remove"] == "":
                    if len(x) == len(y) + 1:
                        y.append(re.findall(f'{dict_filter["filter_y_start"]}('
                                            f'.*?){dict_filter["filter_y_end"]}', line)[0])
                elif re.search(dict_filter["filter_y_remove"], line):
                    pass
                elif len(x) == len(y) + 1:
                    y.append(re.findall(f'{dict_filter["filter_y_start"]}(.*?){dict_filter["filter_y_end"]}', line)[0])

            if re.search(dict_filter["filter_annotate_start"], line):
                if dict_filter["filter_annotate_remove"] == "":
                    if len(x) == len(annotate) + 1:
                        annotate.append(re.findall(
                            f'{dict_filter["filter_annotate_start"]}('
                            f'.*?){dict_filter["filter_annotate_end"]}', line)[0])
                elif re.search(dict_filter["filter_annotate_remove"], line):
                    pass
                elif len(x) == len(annotate) + 1:
                    annotate.append(
                        re.findall(
                            f'{dict_filter["filter_annotate_start"]}('
                            f'.*?){dict_filter["filter_annotate_end"]}', line)[0])
        if len(x) == len(y) + 1:
            if len(x) == len(annotate):
                annotate.pop()
            x.pop()
        if len(x) != 0:
            show_data(x, y, annotate, dict_filter, file_name)


def show_data(x, y, annotate, dict_filter, file_name):
    # print(x, y, annotate)
    x = np.array(x).astype("float")
    y = np.array(y).astype("float")
    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))

    ax1.plot(x, y, color=dict_filter["filter_color"])
    ax1.set_ylim(min(y) - (max(y)-min(y)) * 0.2, max(y)+(max(y)-min(y)) * 0.2)
    ax1.set_title(file_name + '_' + dict_filter["filter_name"], fontsize=20, fontweight="bold")
    ax1.set_xlabel(dict_filter["filter_x_name"], fontsize=20)
    ax1.set_ylabel(dict_filter["filter_y_name"], fontsize=20)
    ax1.set_xlim(x[0], x[-1])
    # 取消坐标轴科学计数法表示
    ax1.get_yaxis().get_major_formatter().set_scientific(False)
    annotate_pre = annotate[0]
    for i in range(len(x)):

        if str(annotate[i]) == str(np.nan):
            continue
        elif i == 0:
            ax1.annotate(annotate[i], xy=(x[i], y[i]), xytext=(0, 10), textcoords='offset points', color='black')
        elif annotate[i] == annotate_pre:
            continue
        else:
            ax1.annotate(annotate[i], xy=(x[i], y[i]), xytext=(0, 10), textcoords='offset points', color='black')
            annotate_pre = annotate[i]

    def onselect(xmin, xmax):
        ax2.cla()
        line2, = ax2.plot([], [], 'o:' + dict_filter["filter_color"], marker='*')
        indmin, indmax = np.searchsorted(x, (xmin, xmax))
        indmax = min(len(x) - 1, indmax)
        region_x = x[indmin:indmax]
        region_y = y[indmin:indmax]
        # print(region_x, region_y, indmax, indmin)
        region_annotate = annotate[indmin:indmax]
        line2.set_data(region_x, region_y)
        ax2.set_xlim(region_x[0], region_x[-1])
        ax2.set_ylim(region_y.min() - (region_y.max()-region_y.min()) * 0.2, region_y.max()+(
                region_y.max()-region_y.min()) * 0.2)
        ax2.set_xlabel(dict_filter["filter_x_name"], fontsize=20)
        ax2.set_ylabel(dict_filter["filter_y_name"], fontsize=20)
        region_annotate_pre = region_annotate[0]

        for i in range(indmax-indmin):
            if str(region_annotate[i]) == str(np.nan):
                continue
            elif i == 0 or i == 1:
                ax2.annotate(region_annotate[i], xy=(region_x[i], region_y[i]), xytext=(
                    0, 10), textcoords='offset points', color='black')
                region_annotate_pre = region_annotate[i]
                # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx%d %d %d ", i,region_x[i],region_y[i])
            elif region_annotate[i] == region_annotate_pre:
                continue
            else:
                ax2.annotate(region_annotate[i], xy=(region_x[i], region_y[i]), xytext=(
                    0, 10), textcoords='offset points', color='black')
                region_annotate_pre = region_annotate[i]
                # print("22222222222222222%d", i)
        # 整数显示横坐标
        ax2.set_xticks(region_x)
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
    load_log_flie()
    