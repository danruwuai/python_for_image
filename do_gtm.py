import numpy as np
from scipy.interpolate import splev, splrep, interp1d
import os
import matplotlib.pyplot as plt


def get_ggm():
    x = [0]
    y = [0]
    ggm_file_path = "jasongamma.csv"
    if os.path.isfile(ggm_file_path):
        print("ggm is", ggm_file_path)
    else:
        return False
    with open(ggm_file_path, "r") as ggm_file:
        for line in ggm_file:
            data_all = line.split("\n")
            data = data_all[0]
            data_ggm = data.split(",")
            x.append(int(data_ggm[0]))
            y.append(int(data_ggm[1]))
    x.append(255)
    y.append(255)
    print(x, y)
    return x, y


def do_ggm(img, bit):
    x, y = get_ggm()
    for i in range(len(x)):
        x[i] = x[i] * 2 ** (bit - 8)
        y[i] = y[i] * 2 ** (bit - 8)
    print(x, y)
    x.append(2**bit - 1)
    y.append(2**bit - 1)
    #fun = splrep(x, y, )
    fun = interp1d(x, y, kind="cubic")
    # print(fun)
    x2 = np.arange(0, 2**bit-1, 1)
    y2 = fun(x2)
    # y2 = splev(x2, fun)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x2, y2)
    plt.show()
    img = np.clip(img, 0, 2**bit - 1)
    img = fun(img)
    # img = splev(img, fun)
    return img




if __name__ == "__main__":
    do_ggm()