# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     aliyunapiconfig
   Description :
   Author :       admin
   date：          2018-12-03
-------------------------------------------------
   Change Activity:
                   2018-12-03:
-------------------------------------------------
"""
__author__ = 'admin_Fred'
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request  import CommonRequest



class ALiYunApiConfig(object):
    def __init__(self, access_key_id, access_key_secret, region_id, set_domain, set_method="POST",
                 set_version="2014-05-15", set_protocol_type="https", set_accept_format="json"):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        self.aliyunapiclient = AcsClient(self.access_key_id, self.access_key_secret, self.region_id)
        self.aliyunrequest = CommonRequest()  # 实例化api

        self.set_domain = set_domain
        self.set_method = set_method
        self.set_version = set_version
        self.set_protocol_type = set_protocol_type
        self.set_accept_format = set_accept_format


        self.aliyunrequest.set_domain(self.set_domain)  # 请求方式
        self.aliyunrequest.set_method(self.set_method)  # 请求方式
        self.aliyunrequest.set_version(self.set_version)  # api版本
        self.aliyunrequest.set_protocol_type(self.set_protocol_type)  # 请求方式 http与https
        self.aliyunrequest.set_accept_format(self.set_accept_format)  # 返回数据类型

    def MResponse(self, code, msg, status):
        dicts = {
            "code": code,
            "msg": msg,
            "status": status,
        }
        return dicts
    # 配置导入
    def Mconfig(self, config):
        for dicts in config: # 获取配置
            for key,value in dicts.items():
                newfunc = getattr(self.aliyunrequest,'add_query_param')
                print(key,value)
                newfunc(key,value)


class ALiYunApiSLB(ALiYunApiConfig):
    '''
    实例API
    '''
    def DescribeLoadBalancers(self, config,):
        '''
        查询已创建的负载均衡实例。
        :param config: [{}]数据类型
        :return: 根据自己配置输出格式
        '''
        self.aliyunrequest.set_action_name('DescribeLoadBalancers')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config不是列表', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response

    def DescribeLoadBalancerAttribute(self, config,):
        '''
        查询指定负载均衡实例的详细信息。
        :param config: [{}]数据类型
        :return: 根据自己配置输出格式
        '''
        self.aliyunrequest.set_action_name('DescribeLoadBalancerAttribute')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response
    '''
    监听API
    '''
    def SetLoadBalancerTCPListenerAttribute(self, config,):
        '''
        修改TCP监听的配置。
        :param config: [{}]数据类型
        :return: 根据自己配置输出格式
        '''
        self.aliyunrequest.set_action_name('SetLoadBalancerTCPListenerAttribute')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response
    '''
    后端服务器API
    '''
    def DescribeVServerGroups(self, config,):
        '''
        查询已创建的服务器组。
        :param config: [{}]数据类型
        :return: 根据自己配置输出格式
        '''
        self.aliyunrequest.set_action_name('DescribeVServerGroups')  # 使用阿里云api方法
        print('DescribeVServerGroups--DescribeVServerGroups---DescribeVServerGroups')
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response


    def DescribeVServerGroupAttribute(self, config,):
        '''
        查询服务器组的详细信息。
        :param config: [{}]数据类型
        :return: 根据自己配置输出格式
        '''
        self.aliyunrequest.set_action_name('DescribeVServerGroups')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response




class ALiYunApiRds(ALiYunApiConfig):
    '''
    查询Rds
    '''
    def DescribeDBInstances(self,config):
        '''
        该接口用于查看实例列表或被RAM授权的实例列表。
        :param config:
        :return:
        '''

        self.aliyunrequest.set_action_name('DescribeDBInstances')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response

    def DescribeDBInstanceAttribute(self,config):
        '''
        该接口用于查看指定实例的详细属性。
        :param config:
        :return:
        '''

        self.aliyunrequest.set_action_name('DescribeDBInstanceAttribute')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response

class ALiYunApiRedis(ALiYunApiConfig):
    '''
    查询阿里云redis信息
    '''
    def DescribeInstances(self,config):
        '''
        调用该API可以查询账户下的某一个或多个实例信息。。
        :param config:
        :return:
        '''

        self.aliyunrequest.set_action_name('DescribeInstances')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)# 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response


    def DescribeInstanceAttribute(self, config):
        '''
        调用该API可以查询账户下的某一个或多个实例信息。。
        :param config:
        :return:
        '''

        self.aliyunrequest.set_action_name('DescribeInstanceAttribute')  # 使用阿里云api方法
        if not isinstance(config, list):
            return self.MResponse(code=20001, msg='config配置不正确', status=False)
        self.Mconfig(config)  # 获取配置
        response = self.aliyunapiclient.do_action_with_exception(self.aliyunrequest)
        return response