# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     kubernets
   Description :
   Author :       admin
   date：          2018-11-28
-------------------------------------------------
   Change Activity:
                   2018-11-28:
-------------------------------------------------
"""
__author__ = 'admin_Fred'
from kubernetes import client

from kubernetes.client.rest import ApiException


class Kubernetesconfig(object):
    def __init__(self, host, cert_file, key_file, verify_ssl=False):
        self.configuration = client.Configuration()  # 为了修改证书配置-如果当前用户的.kube/config证书不对或者权限不够，可以自定义
        self.configuration.host = host  # 连接地址
        self.configuration.verify_ssl = verify_ssl
        self.configuration.cert_file = cert_file  # 配置证书
        self.configuration.key_file = key_file  # 配置证书
        self.configuration.assert_hostname = False


class Kubernetesapi(Kubernetesconfig):

    def mread_namespaced_pod_status(self, name, namespace='default'):
        # 通过namespace获取指定Pod的状态信息
        # obj.mread_namespaced_pod_status(namespace='default',name='wb-user-ms-6f4cf75fb7-4jrfr')
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.read_namespaced_pod_status(namespace=namespace, name=name)
            return api_response
        except ApiException as e:
            return "Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e

    def mlist_node(self):
        # 列出所有node节点信息
        # kcc.mlist_node()
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.list_node()
            return api_response
        except ApiException as e:
            return "Exception when calling CoreV1Api->list_node: %s\n" % e

    def mconnect_get_node_proxy(self, name, path):
        # 列出制定node信息，可以加GET参数
        # obj.mconnect_get_node_proxy(node_name='cn-beijing.i-2zehi88vip2chw6umigv')
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.connect_get_node_proxy(name=name, path=path)
            return api_response
        except ApiException as e:
            return "Exception when calling CoreV1Api->connect_get_node_proxy: %s\n" % e

    def mconnect_patch_node_proxy_with_path(self, name, path):
        '''

        :param name:  node 节点 名称
        :param path:
        :return:
        '''
        # obj.mconnect_patch_node_proxy_with_path(name='test-node2',path='metrics/cadvisor')
        # obj.mconnect_patch_node_proxy_with_path(name='test-node12',path='metrics/cadvisor')
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.connect_patch_node_proxy_with_path(name=name, path=path)
            return api_response
        except ApiException as e:
            return "Exception when calling CoreV1Api->connect_patch_node_proxy_with_path: %s\n" % e

    '''

    deployment 控制器 操作

    '''

    def mlist_namespaced_deployment(self, namespace='default', **kwargs):
        '''
        :param metadata_name:  ALL 所有的deployment，如果需要单独的deployment需要指定deployment的名称
        :param namespace: kubernetes的命名空间
        :return: 返回的是object，里面封装的所有信息
        '''
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.list_namespaced_deployment(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling AppsV1Api->list_namespaced_deployment: %s\n ]" % e

    def mdelete_namespaced_deployment(self, name, namespace, body):
        '''

        :param name:  deployment控制器名称
        :param namespace:
        :param body:
        :return:
        '''
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.delete_namespaced_deployment(name=name, namespace=namespace, body=body)
            return api_response
        except ApiException as e:
            return "Exception when calling AppsV1Api->delete_namespaced_deployment: %s\n" % e

    def mpatch_namespaced_deployment(self, name, namespace, body):

        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
            return api_response
        except ApiException as e:
            return "Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e

    def mread_namespaced_deployment(self, name, namespace='default', **kwargs):
        # obj.mread_namespaced_pod(namespace='default',pod_name='wb-user-ms-6f4cf75fb7-4jrfr')
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.read_namespaced_deployment(namespace=namespace, name=name, **kwargs)
            return api_response
        except ApiException as e:
            return "Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e

    '''

    pod 控制器 操作

    '''

    def mlist_namespaced_pod(self, namespace, **kwargs):

        '''
        :param metadata_name: ALL 所有的 statefulset，如果需要单独的 statefulset 需要指定 statefulset 的名称
        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.list_namespaced_pod(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling CoreV1Api->list_namespaced_pod: %s\n ]" % e

    def mread_namespaced_pod(self, name, namespace='default', **kwargs):
        # obj.mread_namespaced_pod(namespace='default',pod_name='wb-user-ms-6f4cf75fb7-4jrfr')
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.read_namespaced_pod(namespace=namespace, name=name, **kwargs)
            return api_response
        except ApiException as e:
            return "Exception when calling CoreV1Api->read_namespaced_pod: %s\n" % e

    '''

    statefulset 控制器 操作

    '''

    def mread_namespaced_stateful_set(self, name, namespace='default', **kwargs):
        '''

        :param sts_name: statefulset的名称
        :param namespace: kubernetes的命名空间
        :param kwargs: 填写api自有参数
        :return:
        '''
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.read_namespaced_stateful_set(namespace=namespace, name=name, **kwargs)
            return api_response
        except ApiException as e:
            return "Exception when calling AppsV1Api->read_namespaced_stateful_set: %s\n" % e

    def mpatch_namespaced_stateful_set(self, name, namespace, body, **kwargs):
        '''
        obj.mpatch_namespaced_stateful_set(deploy_name=k ,namespace='dev',body=body)
        :param sts_name: statefulset的名称
        :param namespace: kubernetes的命名空间
        :param body: 填写json数据格式，但是必须dump
        :return: 字符串
        '''
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.patch_namespaced_stateful_set(name=name, namespace=namespace, body=body, **kwargs)
            return api_response
        except ApiException as e:
            return "Exception when calling AppsV1Api->patch_namespaced_stateful_set: %s\n" % e

    def mlist_namespaced_stateful_set(self, namespace, **kwargs):
        '''

        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            AppsV1Api = client.AppsV1Api(client.ApiClient(self.configuration))
            api_response = AppsV1Api.list_namespaced_stateful_set(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n ]" % e

    '''
    ingress

    '''

    def mlist_namespaced_ingress(self, namespace, **kwargs):
        '''

        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            ExtensionsV1beta1Api = client.ExtensionsV1beta1Api(client.ApiClient(self.configuration))
            api_response = ExtensionsV1beta1Api.list_namespaced_ingress(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling ExtensionsV1beta1Api->list_namespaced_ingress: %s\n ]" % e

    '''
    service
    '''

    def mlist_namespaced_service(self, namespace, **kwargs):
        '''

        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.list_namespaced_service(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n ]" % e

    '''
    ConfigMaps
    '''

    def mlist_namespaced_config_map(self, namespace, **kwargs):
        '''
        查看configmaps
        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.list_namespaced_config_map(namespace=namespace, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling CoreV1Api->list_namespaced_config_map: %s\n ]" % e

    def mreplace_namespaced_config_map(self, name, namespace, body, **kwargs):
        '''
        替换configmaps配置
        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.replace_namespaced_config_map(namespace=namespace, name=name, body=body, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling CoreV1Api->replace_namespaced_config_map: %s\n ]" % e

    def mdelete_namespaced_config_map(self, name, namespace, body, **kwargs):
        '''
        删除configmaps配置
        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.delete_namespaced_config_map(name=name, namespace=namespace, body=body, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling CoreV1Api->delete_namespaced_config_map: %s\n ]" % e

    def mcreate_namespaced_config_map(self, namespace, body, **kwargs):
        '''
        创建configmaps配置
        :param namespace: kubernetes 的命名空间
        :return: 返回的是 object，里面封装的所有信息
        '''
        try:
            CoreV1Api = client.CoreV1Api(client.ApiClient(self.configuration))
            api_response = CoreV1Api.create_namespaced_config_map(namespace=namespace, body=body, **kwargs)
            return api_response
        except ApiException as e:
            return "[ Exception when calling CoreV1Api->create_namespaced_config_map: %s\n ]" % e


