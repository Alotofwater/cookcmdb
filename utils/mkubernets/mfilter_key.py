# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     glkey
   Description :
   Author :       admin
   date：          2018-12-21
-------------------------------------------------
   Change Activity:
                   2018-12-21:
-------------------------------------------------
__author__ = 'admin_Fred'
"""


def filter_dict_key(data_source,filtering_list):
    data = [data_source]
    while data:
        data_ls = data.pop()  # 获取列表中得数据
        for filter_str in filtering_list:
            # data = [data_source]  # 数据原 转换成 列表  内存地址=
            if isinstance(data,str): # 字符串
                continue
            if isinstance(data_ls, list): # 如果是列表
                for l in data_ls:
                    type_list = isinstance(l, list)
                    # value是字典数据类型
                    type_dict = isinstance(l, dict)
                    # value是字符串数据类型
                    type_str = isinstance(l, str)
                    if type_str:
                        continue
                    if type_list or type_dict:
                        data.append(l)
            if isinstance(data_ls, dict):
                flang = False
                delkeylist = []
                for key in data_ls:  # 循环数据

                    if filter_str == key:
                        # data_ls.pop(key)
                        delkeylist.append(key)
                        flang = True
                    # value是列表数据类型
                    type_dict = isinstance(data_ls.get(key),dict)
                    # value是字符串数据类型
                    type_str = isinstance(data_ls.get(key),str)
                    # 如果value是字符串 - 跳出本次循环
                    if type_str:
                        continue
                    if type_dict:
                        data.append(data_ls.get(key))
                        # print(data_ls.get(key))
                if flang:
                    for delstr in delkeylist:
                        data_ls.pop(delstr)
    return data_source
