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
from utils.maliyun.aliyunapi import ALiYunApiRds

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
aliyunapi = ALiYunApiRds(
    access_key_id=settings.access_key_id,
    access_key_secret=settings.access_key_secret,
    region_id='cn-beijing', # 服务器区域
    set_domain='rds.aliyuncs.com', # api接口
    set_version='2014-08-15'
)



# 查询已创建的Rds配置
RdsList_Config = [
    {'RegionId':'cn-beijing'}, # 实例所属地域ID，通过函数DescribeRegions查看。
    {'PageSize':50}, # 每页记录数，取值：30；50；100；默认值：30。
    {'PageNumber':1}, # 页码，取值为：大于0且不超过Integer数据类型的的最大值，默认值为1。
]




@celery.shared_task(base=TaskStep)
def aliyun_rdslist():
    # 获取rds 列表内容
    rdslist = aliyunapi.DescribeDBInstances(RdsList_Config)

    responsejson = json.loads(rdslist, encoding='utf-8')
    responselist = responsejson.get('Items').get('DBInstance')


    # 获取登陆权限
    cmdbuserinfo = {"username":settings.cmdbusername,"passwd":settings.cmdbpasswd}
    loginret = requests.post('%s/restapi/v1/loginapi/' %(settings.collecturl),json=cmdbuserinfo)
    print('sessionid: %s'%(loginret.cookies.get('sessionid')))
    # 获取服务端返回的sessionid
    sessionid = loginret.cookies.get('sessionid')

    postdict = {'auth':sessionid,'postdata':[]}

    for i in responselist:
        # 获取rds 详细 信息
        DescribeDBInstanceAttributeconfig = [{'DBInstanceId': i.get('DBInstanceId')}]
        rdsattribute = aliyunapi.DescribeDBInstanceAttribute(DescribeDBInstanceAttributeconfig)
        rdsattributejson = json.loads(rdsattribute, encoding='utf-8')
        rdsattributelist = rdsattributejson.get('Items').get('DBInstanceAttribute')[0]

        # print('rdsattributelist %s ' %(rdsattributelist))
        postdata = {
            "DBInstanceDescription": i.get('DBInstanceDescription'), # rds别名-描述
            "DBInstanceId": i.get('DBInstanceId'), # rds 唯一 id
            "ConnectionString": rdsattributelist.get('ConnectionString'), # 连接地址
            "InstancenetWorkType": i.get('InstanceNetworkType'), # rds网络类型
            "Engine": i.get('Engine'), # rds数据库名
            "EngineVersion": i.get('EngineVersion') # rds版本
        }
        postdict.get('postdata').append(postdata)
    print(postdict, len(postdict.get('postdata')))

    responseret = requests.post('%s/restapi/v1/rdsapi/' %(settings.collecturl), json=postdict)
    responsejson = json.loads(responseret.text,encoding='utf-8')
    print(responsejson)

    sessionmodels.Session.objects.filter(session_key=sessionid).delete()  # 采集完毕及时删除 session 会话
    return responsejson


