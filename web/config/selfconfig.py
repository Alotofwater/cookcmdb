# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     memory_list
   Description :
   Author :       admin
   date：          2018-10-25
-------------------------------------------------
   Change Activity:
                   2018-10-25:
-------------------------------------------------
"""
__author__ = 'admin_Fred'


from stark.service.stark import site, StarkConfig, Option, get_choice_text
from django.urls import reverse
from django.utils.safestring import mark_safe
from cmdb_server import settings




class SelfConfig_list_Config(StarkConfig):
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
            val.insert(len(self.list_display),StarkConfig.display_edit_del)
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
    def get_add_btn(self):
        name = "%s:%s" % (self.site.namespace, self.get_add_url_name,)
        permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
        if name in permission_dict:
            return super().get_add_btn()

    def display_create_at_date(self, row=None, header=False):
        if header:
            return '创建时间'
        return row.create_at.strftime('%Y-%m-%d')
    # 生成表格信息
    list_display = [
                    'title',
                    'allocation',
                    'notes',
                    display_create_at_date,
                    ]
    # 搜索条件
    search_list = ["title","notes","create_at"]

    # 组合搜索按钮
    # condition 额外的查询条件
    # field 表的字段名称
    # is_choice True代表是choice选项
    # is_multi True代表M2M多对多 -多选
    # text_func 按钮文本显示 默认显示ORM中的__str__  默认x传入的ORM对象数据
    # value_func url中GET得参数-默认是表的主键   默认x传入的ORM对象数据
    list_filter = [
        # ,text_func=lambda x:x.server_obj,value_func=lambda x:x.server_obj
        # Option(field='server_obj', is_choice=False,is_multi=False,is_show=False), # 不显示-用来Server列表内存连接跳转
    ]
