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
from utils.mkubernets import Kubernetesapi
from utils.common.response import BaseResponse

# 第三方
from ruamel import yaml

from repository.models import K8sConfigmap
import kubernetes
from django.core.cache import cache
import urllib3
import celery
import copy

urllib3.disable_warnings()  # 去除警告

logger = celery.utils.log.get_task_logger('celery_default')

class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行失败'
        k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()

        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行成功'
        k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pk = kwargs.get("pk")
        status = '异步任务重新执行'
        k8singresses_obj = K8sConfigmap.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()


@celery.shared_task(base=TaskStep)
def kubernetes_configmaps(pk):
    response = BaseResponse()  # 返回值用的类
    # pk 数据库主键ID-编辑不条目,id不同
    k8sconfigmap_orm_obj = K8sConfigmap.objects.filter(pk=pk).first()
    # 获取自用配置
    selfconf_content_yaml = k8sconfigmap_orm_obj.content_object.allocation
    selfconf_content_json = yaml.safe_load(selfconf_content_yaml)

    # 存活 失效
    publish_status_id = str(k8sconfigmap_orm_obj.publish_status_id)
    # 发布模式（新老环境发布）
    publish_mode_id = str(k8sconfigmap_orm_obj.publish_mode_id)

    # 新老环境
    newoldtest = ["newtest", "oldtest"]
    # 新环境
    newtest = ["newtest", ]
    # 老环境
    oldtest = ["oldtest", ]

    # 获取 编辑成功的 configmaps 配置文件内容
    content = k8sconfigmap_orm_obj.content
    contentjson = yaml.safe_load(stream=content)  # 转换成json数据
    configname = contentjson.get("metadata").get("name")  # 获取配置文件名

    # 生成修改的configmap配置
    apiVersion = contentjson.get("apiVersion")
    data = contentjson.get("data")
    kind = contentjson.get("kind")
    metadata = contentjson.get("metadata")

    kubecrtdict = {}  # 获取k8s连接配置
    for keyname in newoldtest:  # k8s 新老环境 名字
        kukecltcrtjson = selfconf_content_json.get(keyname)
        # kubecrtdict[keycrt] = kukecltcrt
        ulr = kukecltcrtjson.get("ulr")
        crt = kukecltcrtjson.get("crt")
        key = kukecltcrtjson.get("key")
        namespace = kukecltcrtjson.get("namespace")
        k8sapi = Kubernetesapi(host=ulr, cert_file=crt, key_file=key, )
        kubecrtdict[keyname] = {"k8sapi": k8sapi, "namespace": namespace}
        print("kubecrt %s %s %s %s %s" % (ulr, crt, key, namespace, k8sapi))

    def comfigmap_crud(env_list):
        for oldnewkey in env_list:
            # k8s api 集群入口
            k8sapiobj = kubecrtdict.get(oldnewkey).get("k8sapi")
            mnamespace = kubecrtdict.get(oldnewkey).get("namespace")

            # 查看configmaps配置是否存在
            newfun = getattr(k8sapiobj, 'mlist_namespaced_config_map')
            retfunc = newfun(namespace=mnamespace, field_selector='metadata.name=%s' % (configname))
            # print(retfunc)
            copymetadata = copy.deepcopy(metadata)
            copymetadata["namespace"] = mnamespace
            body = kubernetes.client.V1ConfigMap(
                # 以下赋值都是json数据
                api_version=apiVersion,
                kind=kind,
                metadata=copymetadata,
                data=data
            )
            # 配置文件不存在 创建
            if not retfunc.items and (publish_status_id == "1"):
                # 创建 configmaps 配置文件
                ret = k8sapiobj.mcreate_namespaced_config_map(body=body, namespace=mnamespace)
                # print(ret)
                response.code = 20000
                response.data = content
            # 配置文件存在 修改
            if retfunc.items and (publish_status_id == "1"):
                # 修改 configmaps 配置文件
                ret = k8sapiobj.mreplace_namespaced_config_map(body=body, namespace=mnamespace, name=configname)
                # print(ret)
                response.code = 20000
                response.data = content

            # 失效状态删除configmaps
            if (publish_status_id == "2") and retfunc.items:
                # body = kubernetes.client.V1DeleteOptions(api_version=apiVersion,kind=kind)
                # print('body:::::::::::::::%s' % (body))
                print(k8sapiobj.mdelete_namespaced_config_map(name=configname, namespace=mnamespace, body={}))
                response.code = 20000
                response.data = '删除%s' % (configname)

    # 新老测试环境更新
    if publish_mode_id == "1":  # 新老环境更新
        comfigmap_crud(newoldtest)
        return response.dict
    if publish_mode_id == "2":  # 新环境更新
        comfigmap_crud(newtest)
        return response.dict
    if publish_mode_id == "3":  # 老环境更新
        comfigmap_crud(oldtest)
        return response.dict
    response.data = '%s' % ("未执行任何更新操作")
    return response.dict

