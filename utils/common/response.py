# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     response
   Description :
   Author :       admin
   date：          2018-11-15
-------------------------------------------------
   Change Activity:
                   2018-11-15:
-------------------------------------------------
"""
__author__ = 'admin_Fred'

# response  响应体

class BaseResponse(object):

    def __init__(self):
        self.code = 10000
        self.data = None
        self.error = None

    @property
    def dict(self): # 静态属性字典返回，修改双下划线__dict__
        return self.__dict__

