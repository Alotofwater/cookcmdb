# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     md
   Description :
   Author :       admin
   date：          2018-12-11
-------------------------------------------------
   Change Activity:
                   2018-12-11:
                   __author__ = 'admin_Fred'
-------------------------------------------------
"""

import hashlib


def contentmd5(newcontent,oldcontent):
    md5 = hashlib.md5()  # 创建一个md5算法的对象
    # 取内容中的0到50
    md5.update(newcontent[0:50].encode('utf-8'))  # 接收bytes类型
    return md5.hexdigest()
