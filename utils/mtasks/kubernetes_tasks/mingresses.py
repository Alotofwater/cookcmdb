# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mingresses
   Description :
   Author :       admin
   date：          2018-12-19
-------------------------------------------------
   Change Activity:
                   2018-12-19:
-------------------------------------------------
__author__ = 'admin_Fred'
"""
from __future__ import absolute_import  # 必须发生在文件的开头
# 自己
from utils.mkubernets import Kubernetesapi
from utils.common.response import BaseResponse

# 第三方
from ruamel import yaml
from repository.models import K8sIngresses
from django.core.cache import cache
# python
import urllib3
import re
import celery
import copy
import json

urllib3.disable_warnings()  # 去除警告

logger = celery.utils.log.get_task_logger('celery_default')

class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行失败'
        k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk = kwargs.get("pk")
        status = '异步任务执行成功'
        k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pk = kwargs.get("pk")
        status = '异步任务重新执行'
        k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
        k8singresses_obj.task_status = status
        k8singresses_obj.save()


@celery.shared_task(base=TaskStep)
def kubernetes_ingresses(pk):
    response = BaseResponse()  # 返回值用的类
    # pk 数据库主键ID-编辑不条目,id不同
    k8singresses_obj = K8sIngresses.objects.filter(pk=pk).first()
    # 获取自用配置
    selfconf_content_yaml = k8singresses_obj.content_object.allocation
    selfconf_content_json = yaml.safe_load(selfconf_content_yaml)

    # 存活 失效
    publish_status_id = str(k8singresses_obj.publish_status_id)
    # 发布模式（新老环境发布）
    publish_mode_id = str(k8singresses_obj.publish_mode_id)

    # 获取选择 serviceName
    serviceName = k8singresses_obj.get_ingress_id_display()  # 选择 业务 api 名称
    # 获取提交 需要添加或删除的 url
    urlpath = str(k8singresses_obj.urlpath).replace(" ", "")

    # ingress 名称
    newingressname = '%s-%s' % ("web-ui", serviceName)

    # 新老环境
    newoldtest = ["newtest", "oldtest"]
    # 新环境
    newtest = ["newtest", ]
    # 老环境
    oldtest = ["oldtest", ]

    kubecrtdict = {}  # 获取k8s连接配置
    for keyname in newoldtest:  # k8s 新老环境 名字
        kukecltcrtjson = selfconf_content_json.get(keyname)
        # kubecrt[keycrt] = kukecltcrt
        ulr = kukecltcrtjson.get("ulr")
        crt = kukecltcrtjson.get("crt")
        key = kukecltcrtjson.get("key")

        namespace = kukecltcrtjson.get("namespace")

        # 替换相关配置
        ingressesconfigyaml = yaml.safe_dump(selfconf_content_json.get("ingressesconfig"))
        ingressesconfigyaml = re.subn('replace_name\\b', newingressname, ingressesconfigyaml)  # replace_name
        ingressesconfigyaml = re.subn('replace_namespace\\b', namespace, ingressesconfigyaml[0])  # replace_namespace
        ingressesconfigyaml = re.subn('replace_serviceName\\b', serviceName,
                                      ingressesconfigyaml[0])  # replace_serviceName
        ingressesconfigyaml = re.subn('replace_path\\b', urlpath, ingressesconfigyaml[0])
        ingressesconfigjson = yaml.safe_load(ingressesconfigyaml[0])

        k8sapi = Kubernetesapi(host=ulr, cert_file=crt, key_file=key, )
        kubecrtdict[keyname] = {"k8sapi": k8sapi, "jsonconfig": ingressesconfigjson, "namespace": namespace}
        print("kubecrt %s %s %s %s %s" % (ulr, crt, key, namespace, k8sapi))

    def ingresses_crud(env_list):
        for oldnewkey in env_list:
            # k8s api 集群入口
            k8sapiobj = kubecrtdict.get(oldnewkey).get("k8sapi")
            # 获取已经修改的 配置文件
            jsonconfig = kubecrtdict.get(oldnewkey).get("jsonconfig")
            mnamespace = kubecrtdict.get(oldnewkey).get("namespace")

            # 查看 ingress 配置是否存在
            newfun = getattr(k8sapiobj, 'mlist_namespaced_ingress')
            retfunc = newfun(namespace=mnamespace, field_selector='metadata.name=%s' % (newingressname))

            print("%s %s" % (mnamespace, jsonconfig))


            # 通过 ingress 配置配置文件名 判断是否存在
            if not retfunc.items and (publish_status_id == "1"):  # 配置文件不存在
                # 创建 ingress 配置文件
                print("%s %s" % (mnamespace, jsonconfig))
                print(k8sapiobj.mcreate_namespaced_ingress(body=jsonconfig, namespace=mnamespace))
                print(retfunc.items)
                k8singresses_obj.content = jsonconfig
                k8singresses_obj.save()
                response.code = 20002
                response.data = '%s' % (jsonconfig)

            if retfunc.items:
                # 获取 ingress 配置
                onlinedictjson = retfunc.items[0].to_dict()
                # 获取 paths key 中  url
                onlinepaths = onlinedictjson.get("spec").get("rules")[0].get("http").get("paths")

            if retfunc.items and (publish_status_id == "1"):  # 配置文件存在 修改 配置
                print("%s %s" % (mnamespace, jsonconfig))

                # 复制 数据空中 初始化的ingress 数据
                copyjsonconfig = copy.deepcopy(jsonconfig)
                copyjsonconfig.get("spec").get("rules")[0].get("http")["paths"] = []
                copypaths = copyjsonconfig.get("spec").get("rules")[0].get("http").get("paths")

                searchpath_list = []  # 获取新老 url 后面要将 url 重新添加到 配置中
                # 循环线上配置文件 获取 path
                for i in onlinepaths:
                    # 正则匹配 path 路径
                    old_db_urlpath = str(i.get("path")).replace(" ", "")
                    searchpath_list.append(old_db_urlpath)

                if not urlpath in searchpath_list:  # 不存在列表中
                    searchpath_list.append(urlpath)

                for url in list(set(searchpath_list)):
                    copypaths.append({'backend': {'serviceName': serviceName, 'servicePort': 8080}, 'path': url})
                print(
                    k8sapiobj.mpatch_namespaced_ingress(body=copyjsonconfig, namespace=mnamespace, name=newingressname))
                print("配置文件存在：%s  %s ----- " % ("paths", copyjsonconfig,))

                # 保存已经删除的配置
                k8singresses_obj.content = yaml.safe_dump(copyjsonconfig)
                k8singresses_obj.save()

                response.code = 20002
                response.data = '%s' % (copyjsonconfig)

            # 失效状态删除 ingress
            if (publish_status_id == "2") and retfunc.items:
                print("%s %s" % (mnamespace, jsonconfig))

                # # 复制 数据空中 初始化的ingress 数据
                delcopyjsonconfig = copy.deepcopy(jsonconfig)
                delcopyjsonconfig.get("spec").get("rules")[0].get("http")["paths"] = []
                delcopypaths = delcopyjsonconfig.get("spec").get("rules")[0].get("http").get("paths")

                searchpath_list = []  # 获取新老 url 后面要将 url 重新添加到 配置中
                # 循环线上配置文件 获取 path
                for i in onlinepaths:
                    # 正则匹配 path 路径
                    old_db_urlpath = str(i.get("path")).replace(" ", "")
                    searchpath_list.append(old_db_urlpath)

                if urlpath in searchpath_list:  # 存在列表中,删除该 url
                    searchpath_list.remove(urlpath)

                for url in list(set(searchpath_list)):
                    delcopypaths.append({'backend': {'serviceName': serviceName, 'servicePort': 8080}, 'path': url})
                k8sapiobj.mpatch_namespaced_ingress(name=newingressname, namespace=mnamespace, body=delcopyjsonconfig)

                # 保存已经删除的配置
                k8singresses_obj.content = yaml.safe_dump(delcopyjsonconfig)
                k8singresses_obj.save()

                response.code = 20002
                response.data = '删除 %s ' % (urlpath)

    # 新老测试环境更新
    if publish_mode_id == "1":  # 新老环境更新
        ingresses_crud(newoldtest)
        return response.dict
    if publish_mode_id == "2":  # 新环境更新
        ingresses_crud(newtest)
        return response.dict
    if publish_mode_id == "3":  # 老环境更新
        ingresses_crud(oldtest)
        return response.dict
    if publish_mode_id == "0":  # 必須更新
        raise ValueError('publish_mode_id 选择错误 num %s' % (publish_mode_id))

    return response.dict
