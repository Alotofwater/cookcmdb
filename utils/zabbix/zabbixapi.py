# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     zabbixapi
   Description :
   Author :       admin
   date：          2018-12-15
-------------------------------------------------
   Change Activity:
                   2018-12-15:
-------------------------------------------------
__author__ = 'admin_Fred'
"""
import requests
from ruamel import yaml

class Zabbixconfig(object):
    def __init__(self,
                 zabbixurl,
                 user,
                 passwd,
                 header=None,
                 jsonrpc="2.0",
                 idnum=20001  # 20001 代表操作 登录
                 ):

        self.user = user
        self.passwd = passwd
        self.idnum = idnum

        self.url = zabbixurl
        self.header = header if header == None else {"Content-Type": "application/json"}
        self.jsonrpc = jsonrpc

    def request_info(self, data):
        try:
            # print(data)
            response = requests.post(url=self.url, json=data, headers=self.header).json()
            # print(response)
            return response
        except Exception as e:
            return "Auth Failed, Please Check Your Name And Password: %s" % (e)

    # 获取用户 token
    @property
    def auth_id(self):
        data = {
            "jsonrpc": self.jsonrpc,
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.passwd,
            },
            "id": self.idnum,
        }
        token = self.request_info(data)
        print(token.get('result'))
        return token.get('result')  # 返回 token


    def createconfigjson(self,jsonrpc,method,params,idnum):
        '''
        添加 token
        :param yamlconfig: yaml
        :return: json
        '''
        configjson = {}
        configjson["jsonrpc"] = jsonrpc
        configjson["method"] = method
        configjson["params"] = params
        configjson["id"] = idnum
        configjson["auth"] = self.auth_id
        return configjson



class Zabbixapi(Zabbixconfig):
    '''
    host 主机 api
    '''

    def hostcreate(self, params,jsonrpc="2.0",method="host.create",idnum=3000):
        '''
        创建主机
        :param yamlconfig:
        :return:
        '''
        createjson = self.createconfigjson(
            params=params,
            jsonrpc=jsonrpc,
            method=method,
            idnum=idnum,
        )
        response = self.request_info(createjson)
        return response

    '''
    主机群组
    '''

    def grouphostget(self, params,jsonrpc="2.0",method="hostgroup.get",idnum=4000):
        '''
        查询主机群组
        :param yamlconfig:
        :return:
        '''
        createjson = self.createconfigjson(
            params=params,
            jsonrpc=jsonrpc,
            method=method,
            idnum=idnum,
        )
        response = self.request_info(createjson)
        return response

    '''
    模板
    '''

    def templatescreenget(self, params,jsonrpc="2.0",method="templatescreen.get",idnum=4000):
        '''
        查询模板
        :param yamlconfig:
        :return:
        '''
        createjson = self.createconfigjson(
            params=params,
            jsonrpc=jsonrpc,
            method=method,
            idnum=idnum,
        )
        response = self.request_info(createjson)

        return response






#
#
# zabbixtoconfig = Zabbixapi(zabbixurl='http://192.168.56.11/zabbix/api_jsonrpc.php', user='Admin', passwd='qwe123a')
#
#
# # 创建语句
# createhost = {
#         "host": "testserver1",
#         "interfaces": [
#             {
#                 "type": 1,
#                 "main": 1,
#                 "useip": 1,
#                 "ip": "192.168.3.1",
#                 "dns": "",
#                 "port": "10050"
#             }
#         ],
#         "groups": [
#             {
#                 "groupid": "1"
#             }
#         ],
#         "templates": [
#             {
#                 "templateid": "10001"
#             }
#         ],
#         "inventory_mode": 0,
#         "inventory": {
#             "macaddress_a": "01234",
#             "macaddress_b": "56768"
#         }
#     }
#
# cc = zabbixtoconfig.hostcreate(params=createhost)  # 获取 token
# tt = zabbixtoconfig.grouphostget(params={})  # 获取 token
# xx = zabbixtoconfig.templatescreenget(params={"output":["name",""],"filter": {"templateid":"10001"}})  # 获取 token
# # print(cc)
# print(tt)
# print(xx)
