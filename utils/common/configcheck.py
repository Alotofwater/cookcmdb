# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     server_list
   Description :
   Author :       admin
   date：          2018-10-24
-------------------------------------------------
   Change Activity:
                   2018-10-24:
-------------------------------------------------
"""

from ruamel import yaml

import re




def YamlCheck(yamlcontent):
    '''

    :param yamlcontent:
    :return: # 返回25001 代表有tab符号  # 返回1 代表yaml格式正确
    '''
    try:
        pattern = re.compile('\t')
        tabcheck = pattern.search(yamlcontent)
        if tabcheck:
            return 25001
        yamlcont = yaml.load(yamlcontent)
        return 1
    except Exception as e:
        return e

