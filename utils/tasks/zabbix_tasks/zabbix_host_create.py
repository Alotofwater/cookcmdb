# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     zabbix_host_create
   Description :
   Author :       admin
   date：          2018-12-18
-------------------------------------------------
   Change Activity:
                   2018-12-18:
-------------------------------------------------
__author__ = 'admin_Fred'
"""
from __future__ import absolute_import  # 必须发生在文件的开头

# 第三方
import celery

from utils.mzabbix import Zabbixapi

zabbixtoconfig = Zabbixapi(zabbixurl='http://192.168.56.11/zabbix/api_jsonrpc.php', user='Admin', passwd='qwe123a')

@celery.shared_task()
def hostcreate():

    pass









