# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     tasks.py
   Description :
   Author :       admin
   date：          2018-12-01
-------------------------------------------------
   Change Activity:
                   2018-12-01:
-------------------------------------------------
"""
from __future__ import absolute_import  # 必须发生在文件的开头
# 自己
from utils.kubernetsapi import Kubernetesapi
from utils.response import BaseResponse
from cmdb_server import settings

# 第三方
from ruamel import yaml
from repository import models
import kubernetes
from django.core.cache import cache
import urllib3
import celery
import copy
urllib3.disable_warnings() # 去除警告


class MyTask(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))
    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        print('{0!r} failed: '.format(task_id))
    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

#
# newkubernetesapi = Kubernetesapi(host=settings.kubernets_new_ulr,cert_file=settings.kubernets_new_crt,key_file=settings.kubernets_new_key,)
# oldkubernetesapi = Kubernetesapi(host=settings.kubernets_old_ulr,
#                               cert_file=settings.kubernets_old_crt,
#                               key_file=settings.kubernets_old_key,
#                               )




@celery.shared_task()
def kubernetes_configmaps(postcontent,pk):
    response = BaseResponse() # 返回值用的类
    # pk 数据库主键ID-编辑不条目,id不同
    conn_obj =models.Configcenter.objects.filter(pk=pk).first()
    conftypename = conn_obj.get_conftype_id_display()
    publish_status_id = conn_obj.publish_status_id
    print('asdasdddddddddddddddddddddddddddd%s' % conftypename)

    k8sconfigobj = conn_obj.configrelation.all()
    kubecrt = [] # 获取k8s连接配置
    for i in k8sconfigobj:
        allocationjson = yaml.safe_load(stream=i.allocation)
        kubecrt.append(allocationjson)
    # print(kubecrt)

    # field_selector = field_selector_str



    for k8scrt in kubecrt:
        postcontentjson = yaml.safe_load(stream=postcontent)  # 转换成json数据
        configname = postcontentjson.get("metadata").get("name")  # 获取配置文件名
        print(configname)
        crt = k8scrt.get("crt")
        key =k8scrt.get("key")
        ulr = k8scrt.get("ulr")
        namespace = k8scrt.get("namespace")
        # kubernetes 入口
        k8sapiobj = Kubernetesapi(host=ulr, cert_file=crt,key_file=key, )
        if conftypename == 'configmaps':
            # 生成修改的configmap配置
            apiVersion = postcontentjson.get("apiVersion")
            data = postcontentjson.get("data")
            kind = postcontentjson.get("kind")
            cmetadata = copy.deepcopy(postcontentjson.get("metadata"))
            cmetadata['namespace'] = namespace

            # 查看configmaps配置是否存在
            newfun = getattr(k8sapiobj, 'mlist_namespaced_config_map')
            retfunc = newfun(namespace=namespace,field_selector='metadata.name=%s' %(configname))

            print('namespace::::::::::::::::::::::::::: %s --------- %s' % (cmetadata ,namespace)  )
            body = kubernetes.client.V1ConfigMap(
                # 以下赋值都是json数据
                api_version=apiVersion,
                kind=kind,
                metadata=cmetadata,
                data=data
            )
            # 如果不存在
            if not retfunc.items:
                # 创建 configmaps 配置文件
                k8sapiobj.mcreate_namespaced_config_map(body=body,namespace=namespace)
            else:
                # 如果存在 则 修改 configmaps 配置文件
                k8sapiobj.mreplace_namespaced_config_map(body=body, namespace=namespace, name=configname)
            response.code = 20000
            response.data = postcontent

            # 失效状态删除configmaps
            if (str(publish_status_id) == "2") and retfunc.items:
                # body = kubernetes.client.V1DeleteOptions(api_version=apiVersion,kind=kind)
                # print('body:::::::::::::::%s' % (body))
                k8sapiobj.mdelete_namespaced_config_map(name=configname, namespace=namespace, body={})
                response.code = 20000
                response.data = '删除%s' % (configname)
    return response.dict
