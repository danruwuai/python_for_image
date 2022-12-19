#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#cython: language_level=3
# @time: 2021/5/26 14:17
# @File: create_pyd_file.py
import os
import shutil
import time
import sys


def func(path):
    folder_path = os.path.dirname(path)
    file_path = os.path.split(path)[1]
    os.chdir(folder_path)
    with open('setup.py', 'w') as f:
        f.write('# -*- coding: UTF-8 -*-\n')
        f.write('#cython: language_level=3\n')
        f.write('from setuptools import setup\n')
        f.write('from Cython.Build import cythonize\n')
        f.write('setup(\n')
        f.write("name='test',\n")
        f.write("ext_modules=cythonize('%s')\n" % file_path)
        f.write(")\n")
    os.system('python setup.py build_ext --inplace')
    filename = file_path.split('.py')[0]
    # 删除原有的pyd文件
    if os.path.exists(filename+'.pyd'):
        os.remove('%s.pyd' % filename)
    time.sleep(2)
    # 这里的cp37-win_amd64需要注意一下，这个是依据python解释器类型以及windows版本生成的，建议是单个生成一个pyd文件然后相应修改一下
    os.rename('%s\\%s.cp39-win_amd64.pyd' % (folder_path, filename), '%s\\%s.pyd' % (folder_path, filename))
    os.remove('%s.c' % filename)
    build_folder_path = os.path.join(folder_path, 'build')
    # 删除掉生成的build文件夹
    shutil.rmtree(build_folder_path)
    os.remove('setup.py')
    # 这个是删除py源文件，测试的时候可以先注释掉查看效果
    # os.remove(file_path)


def get_all_file(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.startswith("create_pyd_file") == 0 | name.startswith("main") == 0 | name.startswith("demosaic") == 0 and name.endswith(".py"):
                file_path = os.path.join(root, name)
                func(file_path)

# 获取输入的第一个字符串
#paths = sys.argv[1]
current_working_dir = os.getcwd()
#get_all_file(paths)
get_all_file(current_working_dir)