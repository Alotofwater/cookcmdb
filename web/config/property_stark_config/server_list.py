# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     server_list
   Description :
   Author :       admin
   date：          2018-10-24
-------------------------------------------------
   Change Activity:
                   2018-10-24:
-------------------------------------------------
"""
__author__ = 'admin_Fred'

# 自己
from cmdb_server import settings
from utils.mtasks import hostdelete
from utils.mtasks import hostcreate

import logging

# 第三方
from stark.service.stark import site, StarkConfig, Option, get_choice_text
from django.urls import reverse
from django.utils.safestring import mark_safe
logger = logging.getLogger('django_default')

class Server_list_Config(StarkConfig):
    script_state_add = True  # 添加post请求时，是否触发脚本
    script_state_delete = False  # 删除delete请求时，是否触发脚本
    script_state_change = True  # 修改put请求时，是否触发脚本
    # 删除数据 判断字段状态 是否可以删除
    deletefieldcheckjudge = {"server_status_id":"4"} # ,"hostname":"testcommon002"

    def hookscript_add(self,*args,**kwargs):
        hostname = self.request.POST.get('hostname')
        hostcreate.delay(hostname=hostname)
        # 打印debug日志
        logger.debug(
            'hostname:%s 创建zabbix'
            %(hostname,)
        )
    def hookscript_change(self, *args, **kwargs):
        pk = kwargs.get('pk')
        # 获取服务器状态
        server_status_id = self.request.POST.get('server_status_id')

        if str(server_status_id) == "4":  # 发布执行动作
            hostdelete.delay(pk=pk)  # post请求进来数据，传给异步脚本
            # 打印debug日志
            logger.debug(
                '删除zabbix监控主机配置 pk:%s server_status_id:%s'
                %(pk,
                  server_status_id)
            )

        # url = reverse('stark:repository_k8sresourcecontroller_changelist')
        # return '%s?configmaprelation=%s' % (url, pk)


    def display_memory_record(self, row=None, header=False):  # 自定表格头部
        if header:
            return "内存信息"
        url = reverse('stark:repository_memory_changelist')
        memory_sum = sum([int(i.capacity) for i in row.memory.all()])
        return mark_safe("<a href='%s?server_obj=%s'>%sMB|查看</a>" %(url,row.pk,memory_sum))

    # def display_disk_record(self, row=None, header=False):  # 自定表格头部
    #     if header:
    #         return "硬盘信息"
    #     url = reverse('stark:repository_disk_changelist')
    #     disk_sum = sum([int(i.capacity) for i in row.disk.all()])
    #     return mark_safe("<a href='%s?server_obj=%s'>%sGB|查看</a>" %(url,row.pk,disk_sum))

    # def display_network_record(self, row=None, header=False):  # 自定表格头部
    #     if header:
    #         return "网卡信息"
    #     url = reverse('stark:repository_nic_changelist')
    #     name_show = [i.name for i in row.nic.all()][0]
    #     return mark_safe("<a href='%s?server_obj=%s'>%s|查看</a>" %(url,row.pk,name_show))



    def display_create_at_date(self, row=None, header=False):
        if header:
            return '创建时间'
        return row.create_at.strftime('%Y-%m-%d')
    def display_latest_date_date(self, row=None, header=False):
        if header:
            return '修改时间'
        return row.latest_date.strftime('%Y-%m-%d')

    def get_add_btn(self):
        name = "%s:%s" % (self.site.namespace, self.get_add_url_name,)
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        if name in permission_dict:
            return super().get_add_btn()

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
            val.append(StarkConfig.display_edit_del)
        return val



    def get_action_list(self):
        '''
        根据权限是否隐藏批量执行按钮
        '''
        val = super().get_action_list()
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        del_name = "%s:%s" % (self.site.namespace, self.get_del_url_name,)
        if del_name not in permission_dict:
            val.remove(StarkConfig.multi_delete)

        return val



    # 生成表格信息
    list_display = [
                    "hostname",
                    "os_platform",
                    display_create_at_date, # 创建时间
                    display_latest_date_date, # 修改时间
                    display_memory_record, # 内存
                    # display_disk_record, # 磁盘
                    # display_network_record, # 网卡
                    get_choice_text('server_status_id', '状态')
    ]
    # 搜索条件
    search_list = ["cpu_count","manage_ip",'cabinet_num']

    # 组合搜索按钮
    # condition 额外的查询条件
    # field 表的字段名称
    # is_choice True代表是choice选项
    # is_multi True代表M2M多对多
    # text_func 按钮文本显示 默认显示ORM中的__str__  默认x传入的ORM对象数据
    # value_func url中GET得参数-默认是表的主键   默认x传入的ORM对象数据
    list_filter = [
        Option(field='os_platform', is_choice=False,is_multi=False,text_func=lambda x:x.os_platform,value_func=lambda x:x.os_platform),
        Option(field='server_status_id' ,is_choice=True,is_multi=False, text_func=lambda x:x[1]),
    ]

    action_list = [StarkConfig.multi_delete]