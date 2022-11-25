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
    dict_config={}
    filter_num=[]
    filter_x_start=[]
    filter_x_end=[]
    filter_x_name=[]
    filter_x_remove=[]
    filter_y_start=[]
    filter_y_end=[]
    filter_y_name=[]
    filter_y_remove=[]
    filter_color=[]
    filter_name=[]
    if not os.path.isfile("config.dat"):
        return False
    with open("config.dat", "r") as config_file:
        for line in config_file:
            data_all = line.split("//")
            if data_all[0] == "":
                continue
            data = data_all[0].split("=")
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
    x=[]
    y=[]
    filter_num=dict_config["filter_num"]
    filter_x_start=dict_config["filter_x_start"]
    filter_x_end=dict_config["filter_x_end"]
    filter_x_name=dict_config["filter_x_name"]
    filter_x_remove=dict_config["filter_x_remove"]
    filter_y_start=dict_config["filter_y_start"]
    filter_y_end=dict_config["filter_y_end"]
    filter_y_name=dict_config["filter_y_name"]
    filter_y_remove=dict_config["filter_y_remove"]
    filter_color=dict_config["filter_color"]
    filter_name=dict_config["filter_name"]
    # print(file_log_list)
    print(filter_x_start[0])
    # 循环查找raw的文件
    for file_log in file_log_list:
        with open(file_log, "r") as log_file:
            for line in log_file:
                if re.search(filter_x_start[0], line):                    
                    x.append(re.findall(f'{filter_x_start[0]}(.*?){filter_x_end[0]}', line)[0])
                if re.search(filter_y_start[0], line):                    
                    y.append(re.findall(f'{filter_y_start[0]}(.*?){filter_y_end[0]}', line)[0])
            
    show_data(x, y, filter_x_name[0], filter_y_name[0], filter_color[0], filter_name[0])


def show_data(x, y, x_name, y_name, plt_color, name):
    x = np.array(x).astype("uint32")
    y = np.array(y).astype("uint32")
    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))
    
    ax1.plot(x[:len(y)], y, color = plt_color)
    ax1.set_ylim(min(y)*0.8,max(y)*1.2)
    ax1.set_title(name, fontsize=20, fontweight="bold")
    ax1.set_xlabel(x_name, fontsize=20)
    ax1.set_ylabel(y_name, fontsize=20)
    ax1.set_xlim(x[0] , x[-1])
    line2, = ax2.plot([], [], 'o:r', marker = '*')  # 显示纵坐标*
    def onselect(xmin, xmax):
        indmin, indmax = np.searchsorted(x, (xmin, xmax))
        indmax = min(len(x) - 1, indmax)

        region_x = x[indmin:indmax]
        region_y = y[indmin:indmax]
        line2.set_data(region_x, region_y)
        ax2.set_xlim(region_x[0], region_x[-1])
        ax2.set_ylim(region_y.min() * 0.8, region_y.max() * 1.2)
        ax2.set_xlabel(x_name, fontsize=20)
        ax2.set_ylabel(y_name, fontsize=20)
        # ax2.set_xticks(np.linspace(x[indmin],x[indmax],indmax-indmin,endpoint=True))
        # 整数显示横坐标
        ax2.set_xlim(x[indmin],x[indmax])
        fig.canvas.draw()
    span = SpanSelector(ax1, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='tab:blue'))
    
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()




if __name__ == "__main__":
    load_log_flie()
    