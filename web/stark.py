# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     stark
   Description :
   Author :       admin
   date：          2018-09-27
-------------------------------------------------
   Change Activity:
                   2018-09-27:
-------------------------------------------------
"""
__author__ = 'admin_Fred'

from stark.service.stark import site
from repository import models

from web.config.property_stark_config.server_list import Server_list_Config
from web.config.property_stark_config.memory_list import Memory_list_Config
from web.config.property_stark_config.disk_list import Disk_list_Config
from web.config.property_stark_config.network_list import Network_list_Config
from web.config.property_stark_config.cpu_list import Cpu_list_Config
from web.config.property_stark_config.servicedetailegroup_list import ServiceDetaileGroup_list_Config
from web.config.property_stark_config.servicedetailedlist_list import ServiceDetailedList_list_Config
from web.config.property_stark_config.redislist_list import Redislist_list_Config
from web.config.property_stark_config.rdslist_list import Rdslist_list_Config
from web.config.property_stark_config.applicationlist_list import Applicationlist_list_Config

from web.config.kubernetes_stark_config.k8sconfigmap import K8sConfigmap_list_Config
from web.config.kubernetes_stark_config.k8sconfigmap_admin import K8sConfigmap_list_Config_Admin
from web.config.kubernetes_stark_config.k8sresourcecontroller import K8sResourcecontroller_list_Config
from web.config.kubernetes_stark_config.k8singress import K8sIngress_list_Config
from web.config.kubernetes_stark_config.k8singress_admin import K8sIngress_list_Config_Admin

from web.config.user_stark_config.userprofile_list import UserProfile_list_Config
from web.config.user_stark_config.admininfo_list import AdminInfo_list_Config
from web.config.user_stark_config.usergroup_list import UserGroup_list_Config
from web.config.user_stark_config.businessunit_list import BusinessUnit_list_Config

from web.config.log_stark_config.serverrecord_list import ServerRecord_list_Config
# from web.config.tag_list import Tag_list_Config
from web.config.selfconfig import SelfConfig_list_Config




site.register(model_class=models.UserProfile, stark_config=UserProfile_list_Config) # 用户信息表
site.register(model_class=models.AdminInfo, stark_config=AdminInfo_list_Config) # 用户账号表
site.register(model_class=models.UserGroup, stark_config=UserGroup_list_Config) # 用户组
site.register(model_class=models.BusinessUnit, stark_config=BusinessUnit_list_Config) # 业务线
# site.register(model_class=models.Tag, stark_config=Tag_list_Config) # 资产标签

site.register(model_class=models.Server, stark_config=Server_list_Config) # 主机Server表
site.register(model_class=models.Memory, stark_config=Memory_list_Config) # 内存表
site.register(model_class=models.Disk, stark_config=Disk_list_Config) # 磁盘信息
site.register(model_class=models.Cpu, stark_config=Cpu_list_Config) # Cpu信息
site.register(model_class=models.Network, stark_config=Network_list_Config) # 网络信息


site.register(model_class=models.ServerRecord, stark_config=ServerRecord_list_Config) # 资产变更记录
site.register(model_class=models.SelfConfig, stark_config=SelfConfig_list_Config) # 自用配置文件
site.register(model_class=models.K8sConfigmap, stark_config=K8sConfigmap_list_Config) # k8s configmap文件内容
site.register(model_class=models.K8sConfigmap, stark_config=K8sConfigmap_list_Config_Admin,prev='management') # k8s configmap文件内容 admin 管理员
site.register(model_class=models.K8sResourcecontroller, stark_config=K8sResourcecontroller_list_Config) # kubernetes控制器配置文件
site.register(model_class=models.K8sIngresses, stark_config=K8sIngress_list_Config) # kubernetes Ingresses test环境
site.register(model_class=models.K8sIngresses, stark_config=K8sIngress_list_Config_Admin,prev='management') # kubernetes Ingresses test环境 admin 管理员
site.register(model_class=models.ServiceDetaileGroup, stark_config=ServiceDetaileGroup_list_Config) # 服务组名称
site.register(model_class=models.ServiceDetailedlist, stark_config=ServiceDetailedList_list_Config) # 服务名
site.register(model_class=models.Redislist, stark_config=Redislist_list_Config) # Redis 主机配置  配置文件
site.register(model_class=models.Rdslist, stark_config=Rdslist_list_Config) # Rds 主机配置  配置文件
site.register(model_class=models.Applicationlist, stark_config=Applicationlist_list_Config) # 应用名 配置文件
















