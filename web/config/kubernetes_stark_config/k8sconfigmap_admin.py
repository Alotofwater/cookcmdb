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
__author__ = 'admin_Fred'
"""

# 自定义
from utils.mtasks import kubernetes_configmaps
from utils.common.configcheck import YamlCheck
from cmdb_server import settings
from stark.service.stark import site, StarkConfig, Option, get_choice_text
#


# 第三方
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe
from repository.models import K8sConfigmap
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger('django_default')

class K8sConfigmapForm(forms.ModelForm):
    class Meta:
        model = K8sConfigmap
        # exclude = ['content_type', 'object_id', 'task_status','change_user', 'create_at', 'latest_date']  # 排除的字典
        fields = "__all__"  # 显示所有字段
        # 表单旁边的提示语
        help_texts = {
            'publish_id': '帮助：发布代表保存后直接发布|||不发布代表修改数据将保存到数据里，但不进行发布',
            'publish_mode_id': "帮助：选择在哪个环境发布",
            'publish_status_id': "帮助：存活代表不被删除配置|||失效代表删除配置",

        }

        widgets = {
            'title': forms.TextInput(attrs={'class': "form-control", 'placeholder': '请有含义的名字'}),
            'content': forms.Textarea(attrs={'class': "form-control", 'placeholder': 'yaml格式配置文件内容'}),
            'notes': forms.Textarea(attrs={'class': "form-control", 'placeholder': '必须填写备注-最好有更新记录'}),
            'publish_id': forms.Select(attrs={'class': "form-control", 'placeholder': '必须填写备注-最好有更新记录'}),
        }


    # 验证
    def clean_content(self):
        # 返回25001 代表有tab符号  # 返回1 代表yaml格式正确
        content=self.cleaned_data.get("content")
        yamlcheck = YamlCheck(content)
        print("yamlcheck",yamlcheck)
        if yamlcheck == 25001:
            raise ValidationError("yaml格式不正确: 请把tab 换成 空格" )
        if yamlcheck == 1:
            return content
        else:
            raise ValidationError("yaml格式不正确: %s" %(yamlcheck))






class K8sConfigmap_list_Config_Admin(StarkConfig):
    model_form_class = K8sConfigmapForm

    script_state_add = False  # 添加post请求时，是否触发脚本
    script_state_delete = False  # 删除delete请求时，是否触发脚本
    script_state_change = True  # 修改put请求时，是否触发脚本

    # 删除数据 判断字段状态 是否可以删除
    deletefieldcheckjudge = {"publish_status_id": "2"}  # ,"hostname":"testcommon002"

    def hookscript_change(self, *args, **kwargs):
        pk = kwargs.get('pk')
        # postcontent = self.request.POST.get('content')
        publish_id = self.request.POST.get('publish_id')
        conftype_id = self.request.POST.get("conftype_id")

        print('conftype_id', conftype_id)

        if str(publish_id) == "1":  # 发布执行动作
            kubernetes_configmaps.delay(pk=pk)  # post请求进来数据，传给异步脚本
            logger.debug(
                'pk:%s publish_id:%s content:execute,async,kubernetes_configmaps' % (pk, publish_id))
        logger.debug('pk:%s publish_id:%s content:unexecuted,async' % (pk, publish_id))
        if str(publish_id) == "2":  # 不发布执行动作
            return None # 返回空 stark 组件不会执行 跳转任务
        url = reverse('stark:repository_k8sresourcecontroller_changelist')
        return '%s?configmaprelation=%s' % (url, pk)

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
        # print(val)
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

    def display_latest_date_date(self, row=None, header=False):
        if header:
            return '修改时间'
        return row.latest_date.strftime('%Y-%m-%d')

    # 多对多
    # def display_configrelation(self, row=None, header=False):
    #     if header:
    #         return "更新设置"
    #     configrelation = row.configrelation.all()
    #     class_name_list = [ "%s" %(row.title) for row in configrelation]
    #     return ','.join(class_name_list)
    # 生成表格信息
    list_display = [
        get_choice_text('publish_id', '发布'),
        'title',
        'content',
        "notes",
        'change_user',  # 修改用户
        display_create_at_date,  # 创建时间
        display_latest_date_date,  # 修改时间
        get_choice_text('publish_status_id', '发布状态'),
        'task_status',
    ]

    # 搜索条件
    search_list = ["title", ]

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
        Option(field='publish_status_id', is_choice=True, is_multi=False, text_func=lambda x: x[1]),
    ]

    action_list = [StarkConfig.multi_delete]
