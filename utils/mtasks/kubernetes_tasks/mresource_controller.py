# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mk8sresourcecontroller
   Description :
   Author :       admin
   date：          2018-12-24
-------------------------------------------------
   Change Activity:
                   2018-12-24:
-------------------------------------------------
__author__ = 'admin_Fred'

"""
from __future__ import absolute_import  # 必须发生在文件的开头
# 自己
from utils.mkubernets import Kubernetesapi
from utils.common.response import BaseResponse

# 第三方
from ruamel import yaml
from repository.models import K8sResourcecontroller
from django.core.cache import cache
# python
import re
import celery
import copy
import json

import urllib3
urllib3.disable_warnings()  # 去除警告

logger = celery.utils.log.get_task_logger('celery_default')

class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行失败'
        k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行成功'
        k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pk = kwargs.get("pk")
        status = '异步任务重新执行'
        k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()


@celery.shared_task(base=TaskStep)
def kubernetes_mresource_controller(pk):
    pass






