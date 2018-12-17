# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     host_list
   Description :
   Author :       admin
   date：          2018-12-17
-------------------------------------------------
   Change Activity:
                   2018-12-17:
-------------------------------------------------
"""
__author__ = 'admin_Fred'

from utils.tasks import kubernetes_configmaps
from cmdb_server import settings

# from cmdb_server.settings import log_record

from stark.service.stark import site, StarkConfig, Option, get_choice_text
from django.urls import reverse
from django.utils.safestring import mark_safe

from ruamel import yaml

# import logging
# import os
# file_handle =logging.FileHandler('%s%s%s%s%s' %(settings.BASE_DIR,os.sep,'logs',os.sep, '{logname}server.log'.format(logname='mxddddd')),encoding='utf-8') # 两边同时记录
# settings.log_record.addHandler(file_handle) # 两边同时记录 ，单独记录出一份


class Host_list_Config(StarkConfig):
    script_state_add = False  # 添加post请求时，是否触发脚本
    script_state_delete = False  # 删除delete请求时，是否触发脚本
    script_state_change = True  # 修改put请求时，是否触发脚本

    def hookscript_change(self, *args, **kwargs):
        pk = kwargs.get('pk')
        status = self.request.POST.get('status')


        print('publish_id',status)

        if str(status) =="1": # 发布执行动作---为想好怎么操作控制器，所以不执行脚本
            # 执行异步脚本 ,configcontentormobj=connobj
            # kubernetes_configmaps.delay(postcontent=postcontent,pk=pk)  # post请求进来数据，传给异步脚本
            print('存活',status,pk)
            settings.log_record.debug('pk:%s publish_id:%s content:execute,async,kubernetes_configmaps' % (pk, status ))
        settings.log_record.debug('pk:%s publish_id:%s content:unexecuted,async' % (pk, status))
        # if str(publish_id) == "2": # 不发布执行动作
        #     # postcontent：提交配置内容
        #     kubernetes_configmaps.delay(postcontent=postcontent,pk=pk)  # post请求进来数据，传给异步脚本

    def get_list_display(self):
        '''
        自动判断是否有编辑删除权限的显示
        :return:
        '''
        val = super().get_list_display()
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        edit_name = "%s:%s" % (self.site.namespace, self.get_change_url_name,)
        del_name = "%s:%s" % (self.site.namespace, self.get_del_url_name,)
        if edit_name not in permission_dict:
            val.remove(StarkConfig.display_edit)
            val.remove(StarkConfig.display_checkbox)
        if del_name not in permission_dict:
            val.remove(StarkConfig.display_del)
        if edit_name in permission_dict and del_name in permission_dict:
            val.remove(StarkConfig.display_edit)
            val.remove(StarkConfig.display_del)
            val.insert(len(self.list_display), StarkConfig.display_edit_del)
        return val

    def get_action_list(self):
        '''
        根据权限是否隐藏批量执行按钮
        '''
        val = super().get_action_list()
        # print(val)
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        del_name = "%s:%s" % (self.site.namespace, self.get_del_url_name,)
        if del_name not in permission_dict:
            val.remove(StarkConfig.multi_delete)

        return val

    def get_add_btn(self):
        '''
        添加按钮
        :return:
        '''
        name = "%s:%s" % (self.site.namespace, self.get_add_url_name,)
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        if name in permission_dict:
            return super().get_add_btn()

    def display_create_time_date(self, row=None, header=False):
        if header:
            return '创建时间'
        return row.create_time.strftime('%Y-%m-%d')

    def display_modify_time_date(self, row=None, header=False):
        if header:
            return '修改时间'
        return row.modify_time.strftime('%Y-%m-%d')



    # 生成表格信息
    list_display = [
        get_choice_text('status', '状态'),

        'hostname',
        'i_ip',
        "o_ip",
        'cpu_info',
        'mem_info',
        'disk_info',
        'remarks',
        'instanceid',
        display_create_time_date,  # 创建时间
        display_modify_time_date,  # 修改时间

    ]
    # 搜索条件
    search_list = ["hostname",]

    # 组合搜索按钮
    # condition 额外的查询条件
    # field 表的字段名称
    # is_choice True代表是choice选项
    # is_multi True代表M2M多对多
    # text_func 按钮文本显示 默认显示ORM中的__str__  默认x传入的ORM对象数据
    # value_func url中GET得参数-默认是表的主键   默认x传入的ORM对象数据
    list_filter = [
        # Option(field='os_platform', is_choice=False,is_multi=False,text_func=lambda x:x.os_platform,value_func=lambda x:x.os_platform),
        # Option(field='os_version' ,is_choice=False,is_multi=False,value_func=lambda x:x.os_version ,text_func=lambda x:x.os_version),
        Option(field='status', is_choice=True, is_multi=False, text_func=lambda x: x[1]),
        # Option(field='environment_id', is_choice=True, is_multi=False, text_func=lambda x: x[1] + "环境"),
        # Option(field='configmaprelation', is_choice=False, is_multi=True, is_show=False),  # 不显示-用来 configcenter 配置文件管理的 关联 控制器

    ]

    # 自定义批量执行
    def multi_restart(self, request):
        """
        批量执行重启控制器
        :param request:
        :return:
        """
        id_list = request.POST.getlist('pk')  # [1,2]
        for i in id_list:
            rowobj = self.model_class.objects.filter(pk=i).first()
            print(rowobj.content)

    multi_restart.text = "zabbix监控删除"

    # 批量执行动作按钮添加
    action_list = [StarkConfig.multi_delete,multi_restart]




