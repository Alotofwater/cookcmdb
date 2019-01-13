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


from stark.service.stark import site, StarkConfig, Option, get_choice_text
from django.urls import reverse
from django.utils.safestring import mark_safe
from cmdb_server import settings

import logging
logger = logging.getLogger('django_default')

class ServiceDetailedList_list_Config(StarkConfig):

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
        print(val)
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        del_name = "%s:%s" % (self.site.namespace, self.get_del_url_name,)
        if del_name not in permission_dict:
            val.remove(StarkConfig.multi_delete)

        return val

    # def get_list_display(self):
    #     permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
    #
    #     val = super().get_list_display()
    #     if not permission_dict.get("stark:repository_server_del"):
    #         val.remove(StarkConfig.display_del)
    #
    #     if not permission_dict.get("stark:repository_server_del"):
    #         val.remove(StarkConfig.display_edit)
    #     # val.insert(0, StarkConfig.display_checkbox)
    #     return val

    # 生成表格信息
    list_display = [
                    "title",
                    "servicedetailegroup_obj",
                    get_choice_text('software_type_id', '软件状态'),
                    display_create_at_date, # 创建时间
                    display_latest_date_date, # 修改时间
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
        # Option(field='os_platform', is_choice=False,is_multi=False,text_func=lambda x:x.os_platform,value_func=lambda x:x.os_platform),
        # Option(field='os_version' ,is_choice=False,is_multi=False,value_func=lambda x:x.os_version ,text_func=lambda x:x.os_version),
        # Option(field='server_status_id' ,is_choice=True,is_multi=False, text_func=lambda x:x[1]),
    ]

    action_list = [StarkConfig.multi_delete]