# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    maliyunrdslist
   Description :
   Author :       fred
   date：         2019-01-10
-------------------------------------------------
   Change Activity:
                  2019-01-10:
-------------------------------------------------
"""

from __future__ import absolute_import  # 必须发生在文件的开头
# 自己
from utils.common.response import BaseResponse
from cmdb_server import settings
from utils.maliyun.aliyunapi import ALiYunApiRedis


from django.contrib.sessions import models as sessionmodels  # session表

import celery
import json
import requests

class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行失败'
        # k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()
        #
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行成功'
        # k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pk = kwargs.get("pk")
        status = '异步任务重新执行'
        # k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()




# 连接阿里云Rds配置
aliyunapi = ALiYunApiRedis(
    access_key_id=settings.access_key_id,
    access_key_secret=settings.access_key_secret,
    region_id='cn-beijing', # 服务器区域
    set_domain='r-kvstore.aliyuncs.com', # api接口
    set_version='2015-01-01'
)



# 查询已创建的Rds配置
RdsList_Config = [
    {'RegionId':'cn-beijing'}, # 实例所属地域ID，通过函数DescribeRegions查看。
    {'PageSize':50}, # 每页记录数，取值：30；50；100；默认值：30。
    {'PageNumber':1}, # 分页查询时设置的每页行数，最大值50行，默认值为10。 第几页
]




@celery.shared_task(base=TaskStep)
def aliyun_redislist():
    # 获取rds 列表内容
    redislist = aliyunapi.DescribeInstances(RdsList_Config)

    responsejson = json.loads(redislist, encoding='utf-8')
    print('responsejson',responsejson)
    responselist = responsejson.get('Instances').get('KVStoreInstance')


    # 获取登陆权限
    cmdbuserinfo = {"username":settings.cmdbusername,"passwd":settings.cmdbpasswd}
    loginret = requests.post('%s/restapi/v1/loginapi/' %(settings.collecturl),json=cmdbuserinfo)
    print('sessionid: %s'%(loginret.cookies.get('sessionid')))
    # 获取服务端返回的sessionid
    sessionid = loginret.cookies.get('sessionid')

    postdict = {'auth':sessionid,'postdata':[]}

    for i in responselist:
        # 获取实例详情
        DescribeInstanceAttributeconfig = [{'InstanceId':i.get('InstanceId')}]
        redisattribute = aliyunapi.DescribeInstanceAttribute(DescribeInstanceAttributeconfig)
        redisattributejson = json.loads(redisattribute, encoding='utf-8')
        print('redisattributejson',redisattributejson)
        # 多个或单个redis详细信息
        redisattributedict = redisattributejson.get('Instances').get('DBInstanceAttribute')[0]
        postdata = {
            "InstanceName": i.get('InstanceName'), # redis别名-描述
            "InstanceId": i.get('InstanceId'), # rds 唯一 id
            "ConnectionDomain": redisattributedict.get('ConnectionDomain'), # 连接域名。
            "PrivateIp": redisattributedict.get('PrivateIp'), # 私有IP
            "NetworkType": redisattributedict.get('NetworkType'), # 网络类型 CLASSIC（经典网络） VPC（VPC网络）
            "Engine": redisattributedict.get('Engine'), # 数据库类型。
            "EngineVersion": redisattributedict.get('EngineVersion') # redis版本
        }
        postdict.get('postdata').append(postdata)
    print(postdict, len(postdict.get('postdata')))


    responseret = requests.post('%s/restapi/v1/redisapi/' %(settings.collecturl), json=postdict)
    responsejson = json.loads(responseret.text,encoding='utf-8')
    print(responsejson)

    sessionmodels.Session.objects.filter(session_key=sessionid).delete() # 采集完毕及时删除 session 会话
    return responsejson



