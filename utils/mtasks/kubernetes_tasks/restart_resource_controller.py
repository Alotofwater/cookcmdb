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
from repository.models import K8sResourcecontroller
# from django.core.cache import cache

# python
import urllib3
import celery
import copy
import json
urllib3.disable_warnings()  # 去除警告


logger = celery.utils.log.get_task_logger('celery_default')


class TaskStep(celery.Task):
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(kwargs)
        # 保存执行状态 到
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk_list = kwargs.get("pk_list")
        status = '异步任务执行失败'
        for pk in pk_list:
            k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
            k8singresses_obj.task_status = status
            k8singresses_obj.save()

    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        print(kwargs)
        # taskobj = TaskResult.objects.filter(task_id=task_id).first()
        pk_list = kwargs.get("pk_list")
        status = '异步任务执行成功'
        for pk in pk_list:
            k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
            k8singresses_obj.task_status = status
            k8singresses_obj.save()

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print(kwargs)
        pk_list = kwargs.get("pk_list")
        status = '异步任务重新执行'
        for pk in pk_list:
            k8singresses_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
            k8singresses_obj.task_status = status
            k8singresses_obj.save()


@celery.shared_task(base=TaskStep)
def kubernetes_restart_resource_controller(pk_list):
    response = BaseResponse()  # 返回值用的类
    # 获取ORM数据字典
    k8s_resource_controller_obj_dict = {}

    # pk 数据库主键ID-编辑不条目,id不同
    for pk in pk_list:
        k8s_resource_controller_obj = K8sResourcecontroller.objects.filter(pk=pk).first()
        k8s_resource_controller_obj_dict[str(pk)] = {"orm_obj":k8s_resource_controller_obj,
                                                     "ormfkuserprofile":None
                                                     }

    # 所有环境
    all_crt_list = ["newtest", "oldtest"]

    # 配置模式
    conftype_dict = {
        "2": {
            "conftypename": "daemonsets",
            "choices": "2",
            "select_func_str": "mlist_namespaced_daemon_set",
            "action_func_str": "mpatch_namespaced_daemon_set"
        },
        "3": {
            "conftypename": "deployments",
            "choices": "3",
            "select_func_str": "mlist_namespaced_deployment",
            "action_func_str": "mpatch_namespaced_deployment"
        },
        "4": {
            "conftypename": "statefulsets",
            "choices": "4",
            "select_func_str": "mlist_namespaced_stateful_set",
            "action_func_str": "mpatch_namespaced_stateful_set"
        }
    }

    # 新老环境
    newoldtest = ["newtest", "oldtest"]
    # 新环境
    newtest = ["newtest", ]
    # 老环境
    oldtest = ["oldtest", ]

    kubecrtdict = {}  # 获取k8s连接配置

    for pk in pk_list:

        # ORM 对象
        k8s_resource_controller_obj = k8s_resource_controller_obj_dict.get(str(pk)).get("orm_obj")

        # 获取自用配置
        selfconf_content_yaml = k8s_resource_controller_obj.content_object.allocation
        selfconf_content_json = yaml.safe_load(selfconf_content_yaml)

        # 获取配置内容
        contentyaml = k8s_resource_controller_obj.content
        contentjson = yaml.safe_load(contentyaml)
        # replicas_num = contentjson.get("spec").get("replicas")  # {"spec": {"replicas": 2}}
        controller_name = contentjson.get("metadata").get("name")

        # 存活 失效
        publish_status_id = str(k8s_resource_controller_obj.publish_status_id)
        conftype_id = str(k8s_resource_controller_obj.conftype_id)

        # 发布模式（新老环境发布）
        publish_mode_id = str(k8s_resource_controller_obj.publish_mode_id)

        for keyname in all_crt_list:  # k8s 新老环境 名字
            kukecltcrtjson = selfconf_content_json.get(keyname)
            # kubecrt[keycrt] = kukecltcrt
            ulr = kukecltcrtjson.get("ulr")
            crt = kukecltcrtjson.get("crt")
            key = kukecltcrtjson.get("key")

            namespace = kukecltcrtjson.get("namespace")

            k8sapi = Kubernetesapi(host=ulr, cert_file=crt, key_file=key, )
            kubecrtdict[keyname] = {"k8sapi": k8sapi,
                                    "replicas_json": {"spec": {"replicas": 0}},
                                    "publish_status_id": publish_status_id,  # 存活 失效
                                    "publish_mode_id": publish_mode_id,  # 发布模式（新老环境发布）1 2 3
                                    "conftype": conftype_dict.get(conftype_id),
                                    "controller_name": controller_name,
                                    "namespace": namespace,
                                    }

            # print("kubecrt %s %s %s %s %s" % (ulr, crt, key, namespace, k8sapi))
    # print("kubecrtdict %s" % (kubecrtdict))

    def restart_resource_controller(env_list, select_func_str, action_func_str):
        for oldnewkey in env_list:
            # k8s api 集群入口
            k8sapiobj = kubecrtdict.get(oldnewkey).get("k8sapi")

            # 获取修改配置
            replicas_json = kubecrtdict.get(oldnewkey).get("replicas_json")
            controller_name = kubecrtdict.get(oldnewkey).get("controller_name")
            mnamespace = kubecrtdict.get(oldnewkey).get("namespace")

            # 查看 ingress 配置是否存在
            select_func = getattr(k8sapiobj, select_func_str)
            ret_select_func = select_func(namespace=mnamespace, field_selector='metadata.name=%s' % (controller_name))

            # 配置文件存在
            if ret_select_func.items:
                # 获取 controller(控制器)  配置
                onlinedictjson = ret_select_func.items[0].to_dict()
                copyreplicas_json = copy.deepcopy(replicas_json)

                # 执行动作
                action_func = getattr(k8sapiobj, action_func_str)
                # replicas 改为 0
                action_func(name=controller_name, namespace=mnamespace, body=replicas_json)
                # print("ret_action_func %s" %(ret_action_func))

                # 获取 当前线上 replicas 的数量
                online_replicas_num = onlinedictjson.get("spec").get("replicas")
                copyreplicas_json.get("spec")["replicas"] = int(online_replicas_num)

                # replicas 改为 online_replicas_num
                action_func(name=controller_name, namespace=mnamespace, body=copyreplicas_json)
                # print("ret_action_func %s" % (ret_action_func))

                print("当前配置replicas %s 正式配置replicas %s" %(replicas_json, copyreplicas_json))
                response.data = "xxczxczxczxczxc"
            if not ret_select_func.items:
                response.data = " %s yaml 配置文件不存在 %s" %(controller_name,mnamespace)


    # # 新老测试环境更新
    for keyname in all_crt_list:

        # 获取每个控制器 中的 配置文件
        okubecrtdict = kubecrtdict.get(keyname)
        # 获取 每个 控制器 发布 模式
        opublish_mode_id = okubecrtdict.get("publish_mode_id")
        opublish_status_id = okubecrtdict.get("publish_status_id")

        # 配置文件类型
        oconftype = okubecrtdict.get("conftype")

        # 查询动作
        oconftypename_select_func_str = oconftype.get("select_func_str")
        # 执行动作
        oconftypename_action_func_str = oconftype.get("action_func_str")

        print("for 检查： 详细配置：%s 发布模式：%s 存活失效：%s 配置类型：%s 查询动作：%s 执行动作：%s" % (
            okubecrtdict, opublish_mode_id, opublish_status_id, oconftype, oconftypename_select_func_str,
            oconftypename_action_func_str))


        if opublish_mode_id == "1" and opublish_status_id == "1":  # 新老环境更新
            restart_resource_controller(env_list=newoldtest, select_func_str=oconftypename_select_func_str,
                                      action_func_str=oconftypename_action_func_str)

            print("检查新老环境更新： %s %s %s %s %s %s" % (
            okubecrtdict, opublish_mode_id, opublish_status_id, oconftype, oconftypename_select_func_str,
            oconftypename_action_func_str))
            return response.dict


        if opublish_mode_id == "2" and opublish_status_id == "1":  # 新环境更新
            restart_resource_controller(env_list=newtest, select_func_str=oconftypename_select_func_str,
                                        action_func_str=oconftypename_action_func_str)

            print("检查新环境更新： %s %s %s %s %s %s" % (
            okubecrtdict, opublish_mode_id, opublish_status_id, oconftype, oconftypename_select_func_str,
            oconftypename_action_func_str))
            return response.dict


        if opublish_mode_id == "3" and opublish_status_id == "1":  # 老环境更新
            restart_resource_controller(env_list=oldtest, select_func_str=oconftypename_select_func_str,
                                        action_func_str=oconftypename_action_func_str)

            print("检查老环境更新： %s %s %s %s %s %s" % (
            okubecrtdict, opublish_mode_id, opublish_status_id, oconftype, oconftypename_select_func_str,
            oconftypename_action_func_str))

            return response.dict


        if opublish_mode_id == "0" and opublish_status_id == "1":  # 必須更新
            raise ValueError('publish_mode_id 选择错误 num %s' % (opublish_mode_id))

    return response.dict
