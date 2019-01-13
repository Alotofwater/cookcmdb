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

# 自己

from utils.mzabbix import Zabbixapi
from utils.common.response import BaseResponse

# 第三方
import celery
from ruamel import yaml
from repository.models import Server

# 注册日志
logger = celery.utils.log.get_task_logger('celery_default')

zabbixtoconfig = Zabbixapi(zabbixurl='http://127.0.0.1:8865/api_jsonrpc.php', user='Admin', passwd='zabbix')


class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        # status = '异步任务执行失败'
        # k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()
        logger.info('zabbix主机删除 任务失败时执行:%s pk:%s' % (task_id, pk))

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        # status = '异步任务执行成功'
        # k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()
        logger.info('zabbix主机删除 任务成功时执行:%s pk:%s' % (task_id, pk))

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pk = kwargs.get("pk")
        # status = '异步任务重新执行'
        # k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        # k8singresses_obj.task_status = status
        # k8singresses_obj.save()
        logger.info('zabbix主机删除 任务重试时执行:%s pk:%s' % (task_id, pk))


@celery.shared_task(base=TaskStep)
def hostdelete(pk):
    response = BaseResponse()  # 返回值用的类
    server_obj = Server.objects.filter(pk=pk).first()
    hostname = str(server_obj.hostname)

    # 查询zabbix主机配置信息
    hostgetconfig = {
        "output": "extend",
        "filter": {
            "host": [
                hostname,
            ]
        }
    }

    hostget_ret = zabbixtoconfig.hostget(params=hostgetconfig)
    result_list = hostget_ret.get('result')
    delete_config = []  # zabbix删除配置
    # 获取查询zabbix主机数据 hostid
    for i in result_list:
        delete_config.append(i.get('hostid'))

    delete_ret = zabbixtoconfig.hostdelete(params=delete_config)
    logger.debug('delete_ret:%s hostname:%s pk:%s delete_config:%s deletestr:%s ' % (delete_ret, hostname, pk, delete_config, delete_ret))
    response.code = 20000
    response.data = delete_ret
    return response.dict