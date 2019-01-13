[TOC]


# cookcmdb 资产管理平台

**仔细看如何创建属于自己的插件！**

cookcmdb 优势在于：  
把数据库的每张表当作一个插件功能去写！
python语言编写大家常用django框架，如果使用go语言蓝鲸自定义开发是需要成本的！   
封装事件触发：对数据库进行增删改可以指定触发事件  
封装RBAC权限管理：批量增删改权限  
封装Url-Path：无需管理Url路径问题  
封装强壮查询功能: 代码使用者只需要填写字段名，将其配置，即模糊搜该字段+配合二级分类  
封装统一WebUI界面：填写配置自定义显示表中哪些数据


## 前提条件
- 熟悉python语法
- 熟悉cookcmdb代码相关配置
- 熟悉ORM语句
- 简单数据库设计能力

## 主要组件
- Django==1.11.15
- celery==4.2.0
- redis当消息队列
- mysql5.6

## 功能

- 根据 Django ORM 自动创建web页面与URL 
- 插件执行的异步任务

## web界面插件语法
**使用者需要有一个思想，尽可能把数据拆分到不同表中，表于表之间做关联。**  


- modeles.Server表设计



<python>


    class Server(models.Model):
        """
        服务器信息
        """
    
        business_unit = models.ManyToManyField('BusinessUnit', verbose_name="业务线(部门)", blank=True)
    
        server_status_choices = (
            (1, '上架'),
            (2, '在线'),
            (3, '离线'),
            (4, '下架'),
        )
        server_status_id = models.IntegerField(choices=server_status_choices, default=1, verbose_name='状态')
    
        hostname = models.CharField(max_length=128, unique=True, verbose_name='主机名')
    
        alias = models.CharField(max_length=128, blank=True, verbose_name='别名')
    
        solehostid = models.CharField(max_length=128, blank=True, unique=True, verbose_name='唯一ID')
    
        os_platform = models.CharField(max_length=64, null=True, blank=True, verbose_name='系统/版本')
    
        create_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name="创建时间")
    
        latest_date = models.DateTimeField(null=True, auto_now=True, blank=True, verbose_name="最后修改时间")
    
        class Meta:
            verbose_name_plural = "06服务器表"
    
        def __str__(self):
            return self.hostname
</python>

- modeles.Disk设计


<python>


    # 每个公司需要的硬盘信息不同，粗略设计    
    class Disk(models.Model):
        """
        硬盘信息
        """
        health = models.CharField(max_length=8, verbose_name='健康情况')
        model = models.CharField(max_length=128, verbose_name='磁盘型号')
        capacity = models.FloatField(verbose_name='磁盘容量GB')
        pd_type = models.CharField(max_length=32, verbose_name='磁盘类型')
        server_obj = models.ForeignKey('Server', related_name='disk', verbose_name="主机名")
    
        class Meta:
            verbose_name_plural = "08硬盘表"
    
        def __str__(self):
            return "%s-%s" % (self.server_obj, self.model) # server表中表格中显示内容
</python>

- 主机列表的Web界面生成代码   
该代码需要根据自己需求进行改造，也可以使用默认
<python>

    
    # 自己
    from cmdb_server import settings # 个别配置放在django中settings文件中
    # 
    from utils.mtasks import hostdelete # 机器添加增加监控 - 和 zabbix 自发现一样（不过能改成添加监控项）
    from utils.mtasks import hostcreate

    import logging

    # 第三方
    # 导入web页面显示必备的模块
    from stark.service.stark import site, StarkConfig, Option, get_choice_text
     rom django.urls import reverse
    from django.utils.safestring import mark_safe
    logger = logging.getLogger('django_default') # 日志记录
    
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
        
        # 在主机列表页面 跳转 到 硬盘表 会自动把关于该主机硬盘信息列出（因为磁盘表每一条信息都关联着一条主机信息）   
        def display_disk_record(self, row=None, header=False):  # 自定表格头部
            if header:
                return "硬盘信息"
            url = reverse('stark:repository_disk_changelist')
            disk_sum = sum([int(i.capacity) for i in row.disk.all()])
            return mark_safe("<a href='%s?server_obj=%s'>%sGB|查看</a>" %(url,row.pk,disk_sum))
        
        
        # 在主机列表页面 跳转 到 内存表 会自动把关于该主机内存信息列出（因为磁盘表每一条信息都关联着一条主机信息）
        def display_network_record(self, row=None, header=False):  # 自定表格头部
            if header:
                return "网卡信息"
            url = reverse('stark:repository_nic_changelist')
            name_show = [i.name for i in row.nic.all()][0]
            return mark_safe("<a href='%s?server_obj=%s'>%s|查看</a>" %(url,row.pk,name_show))
    
    
        # mysql 数据库 datetime 类型 需要在这转换一下
        def display_create_at_date(self, row=None, header=False):
            if header:
                return '创建时间'
            return row.create_at.strftime('%Y-%m-%d')
        def display_latest_date_date(self, row=None, header=False):
            if header:
                return '修改时间'
            return row.latest_date.strftime('%Y-%m-%d')
        
        # （以下假设不写按钮权限方法，该主机页面所有按钮都会显示出来，没有权限用户点击，只是提示没有权限！ 
        为了让没有权限的用户看不到该按钮特意添加）
        
        # 判断用户是否显示添加按钮
        def get_add_btn(self):
            name = "%s:%s" % (self.site.namespace, self.get_add_url_name,)
            permission_dict = self.request.session.get(settings.PERMISSION_SESSION_KEY)
            if name in permission_dict:
                return super().get_add_btn()
        
        # 判断 用户 是否有编辑 删除  按钮 根据不同权限显示不同按钮
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
        # 特别注意：
        # CharField类型： 填写表字段名 表头通过models中 verbose_name="主机名" 当作表头
        # DateTimeField类型：需要写自定义方法给其设于表头于表内容显示，起码时间转换 
        # ForeignKey：外键 关联 表头 verbose_name="XXX"
        # class Disk(models.Model): 
        #    def __str__(self): # 显示表格内容信息
        #        return "%s-%s" % (self.server_obj, self.model)


        list_display = [
                        "hostname",
                        "os_platform",
                        display_create_at_date, # 创建时间
                        display_latest_date_date, # 修改时间
                        display_memory_record, # 内存
                        display_disk_record, # 磁盘
                        display_network_record, # 网卡
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
        
        # web界面中有一个单独执行任务接口 
            # 自定义操作
            

        action_list = [StarkConfig.multi_delete] # 在类中封装批量删除
</python>

- 激活使用 Web   
./web/config/存放 主机列表的Web界面生成代码 是否存在这里根据自己喜好  
./web/stark.py # 注意这里必须填写正确

<python>

    # 建表ORM语句
    from repository import models
    from web.config.property_stark_config.server_list import Server_list_Config
    # 注意填写 model_class=主机表 stark_config=刚编写主机列表的Web界面生成代码
    site.register(model_class=models.Server, stark_config=Server_list_Config) # 主机Server表
    最后登陆页面添加视图的权限就好了
     
   
    
</python>


## kubernetes 操作插件
比如kubernetes中 configmaps 配置修改  
首先设计configmaps插件的表  
根据业务场景设计表结构（比如：发布选项/更新环境）

- kubernetes configmaps表设计

<python>



    class K8sConfigmap(models.Model):
        """
        配置文件内容
        """
        # 看的名字就应该明白了，写 celery 异步任务时候通过 该字段判断是否执行
        publish_choices = (
            (1, '发布'),
            (2, '不发布'),
        )
        publish_id = models.IntegerField(verbose_name='是否发布', choices=publish_choices, default=2)  # 是否发布
        
        # 更新环境，在web页面显示字符串内容
        publish_mode_choices = (
            (0, '必须选择'),
            (1, '自建kubernetes'),
            (2, '阿里云kubernetes'),
        )
        publish_mode_id = models.IntegerField(verbose_name='更新环境', choices=publish_mode_choices, default=0)  # 是否发布
    
        title = models.CharField(verbose_name="配置名", max_length=64)
        content = models.TextField(verbose_name="配置内容", )
        notes = models.TextField(verbose_name="备注", null=True, blank=True)
    
        create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
        latest_date = models.DateTimeField(verbose_name="修改时间", null=True, auto_now=True)
        publish_status_choices = (
            (1, '存活'),
            (2, '失效'),
        )
        publish_status_id = models.IntegerField(verbose_name='配置文件状态', choices=publish_status_choices, default=1)  # 状态
    
        change_user = models.ForeignKey('UserProfile', null=True, blank=True, verbose_name="修改人")  # 修改人
        
        # 用于关联控制器 configmap修改 完毕后 跳转 kubernetes 控制器 页面
        content_type = models.ForeignKey(ContentType, verbose_name='关联自用配置', blank=True,
                                         default=22)  # 为了减少  ManyToManyField 关联配置文件
        
        # kubernetes 配置文件关联 我自建单独创建 自动配置文件
        object_id = models.PositiveIntegerField(verbose_name='关联表主键ID', blank=True, default=4)
        content_object = GenericForeignKey('content_type', 'object_id')
        
        # 执行异步任务 状态 每次执行完毕 异步 任务 状态 会写入进来
        task_status = models.CharField(verbose_name="异步任务状态", max_length=128, null=True, blank=True)  # 异步任务状态
    
        class Meta:
            verbose_name_plural = "09configmap配置文件内容"
    
        def __str__(self):
            return self.title
                
               
</python>


- configmaps Web页面

<python>
            
    
    from utils.mtasks import kubernetes_configmaps # kubernetes configmps 修改
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
    
    
    # form表单设计 其实不用编写 只是繁琐 增加 校验

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


    
</python>


- 激活使用 Configmaps   
./web/config/存放 主机列表的Web界面生成代码 是否存在这里根据自己喜好  
./web/stark.py # 注意这里必须填写正确

<python>

    # 建表ORM语句
    from repository import models
    from web.config.kubernetes_stark_config.k8sconfigmap import K8sConfigmap_list_Config    # 注意填写 model_class=主机表 stark_config=刚编写主机列表的Web界面生成代码
    # model_class=ORM语句模块 stark_config=刚编写K8sconfigmaps 代码页面 prev=Url添加字符串 用于同一张表 有多个URL 每个URL 都可以有自个的代码设计，都在 处理同一张表
    site.register(model_class=models.K8sConfigmap, stark_config=K8sConfigmap_list_Config_Admin,prev='management') # k8s configmap文件内容 admin 管理员
    最后登陆页面添加视图的权限就好了
     
   
    
</python>

## 目录介绍


├── celeryrun.sh  启动celery脚本问价   
├── client_api  即将作废   
├── cmdb_server  django配置目录  
├── logs  日志目录  
├── manage.py   
├── mrest_api  api接口目录  
├── rbac    权限组件    
├── repository  专门存放ORM建表语句  
├── requirements.txt  依赖包组  
├── stark   封装增删改查组件     
├── templates   前端代码  
├── utils   通用工具类  
└── web   作为插件存放目录（重要：会了插件编写想展示页面就在这个注册一下）  

## 程序部署
- Dockerfile




## 注意


- QQ
75056082 # 有什么建议，请及时联系！  
**cookcmdb：已在公司使用，公司开发插件我就不提交！争取做开源**   
**只会告诉大家如果快速搭建自己cmdb做到运维链路闭合！**

