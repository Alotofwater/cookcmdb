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

# from repository import models
# from stark.service.stark import site, StarkConfig, Option, get_choice_text
#
# class DepartmentConfig(StarkConfig):
#     list_display = ['idc', 'cabinet_num', StarkConfig.display_edit, StarkConfig.display_del]
#
# site.register(models.Server, DepartmentConfig)
from stark.service.stark import site, StarkConfig,get_choice_text
from repository import models
from web.config.server_list import Server_list_Config
from web.config.memory_list import Memory_list_Config
from web.config.userprofile_list import UserProfile_list_Config
from web.config.admininfo_list import AdminInfo_list_Config
from web.config.usergroup_list import UserGroup_list_Config
from web.config.businessunit_list import BusinessUnit_list_Config
from web.config.tag_list import Tag_list_Config
from web.config.idc_list import IDC_list_Config
from web.config.disk_list import Disk_list_Config
from web.config.nic_list import NIC_list_Config
from web.config.serverrecord_list import ServerRecord_list_Config
from web.config.selfconfig import SelfConfig_list_Config
from web.config.configcenter import Configcenter_list_Config
from web.config.resourcecontroller import Resourcecontroller_list_Config
from web.config.host_list import Host_list_Config




site.register(models.UserProfile, UserProfile_list_Config) # 用户信息表
site.register(models.AdminInfo, AdminInfo_list_Config) # 用户账号表
site.register(models.UserGroup, UserGroup_list_Config) # 用户组
site.register(models.BusinessUnit, BusinessUnit_list_Config) # 业务线
site.register(models.Tag, Tag_list_Config) # 资产标签
site.register(models.IDC, IDC_list_Config) # IDC资料
site.register(models.Server, Server_list_Config) # 主机Server表
site.register(models.Memory, Memory_list_Config) # 内存表
site.register(models.Disk, Disk_list_Config) # 磁盘信息
site.register(models.NIC, NIC_list_Config) # 网卡信息
site.register(models.ServerRecord, ServerRecord_list_Config) # 资产变更记录
site.register(models.SelfConfig, SelfConfig_list_Config) # 自用配置文件
site.register(models.Configcenter, Configcenter_list_Config) # 配置文件内容
site.register(models.Resourcecontroller, Resourcecontroller_list_Config) # kubernetes控制器配置文件
site.register(models.Host, Host_list_Config) # Host 主机表


















