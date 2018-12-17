from django.db import models
from rbac.models import UserInfo as RbacUserInfo
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


# from rbac.models import Role

class UserProfile(models.Model):
    """
    用户信息，运维管理员和业务负责人 50 人
    """
    name = models.CharField('姓名', max_length=32)
    email = models.EmailField('邮箱')
    phone = models.CharField('座机', max_length=32)
    mobile = models.CharField('手机', max_length=32)

    class Meta:
        verbose_name_plural = "01用户信息表"

    def __str__(self):
        return self.name


class AdminInfo(RbacUserInfo):
    """
    用户登录： 10
    """
    user = models.OneToOneField("UserProfile")
    username = models.CharField('用户名', max_length=32)
    password = models.CharField('密码', max_length=32)

    class Meta:
        verbose_name_plural = "02账号密码表"

    def __str__(self):
        return self.username


class UserGroup(models.Model):
    """
    用户组
    ID   名称
     1   组A
     2   组B
     3   组C
    用户组和用户关系表
    组ID    用户ID
     1       1
     1       2
     2       2
     2       3
     3       4
    """
    name = models.CharField(max_length=32, verbose_name='用户组', unique=True)
    users = models.ManyToManyField('UserProfile', verbose_name='用户')

    class Meta:
        verbose_name_plural = "03用户组表"

    def __str__(self):
        return self.name


class BusinessUnit(models.Model):
    """
    业务线(部门)
    """
    name = models.CharField('业务线', max_length=64, unique=True)  # 销售，1,2
    contact = models.ForeignKey(UserGroup, verbose_name="业务线联系人", related_name='c')  # 业务线联系人：1
    manager = models.ForeignKey(UserGroup, verbose_name="运维管理人员", related_name='m')  # 运维管理人员：2

    class Meta:
        verbose_name_plural = "04业务线表"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    资产标签
    """
    name = models.CharField('标签', max_length=32, unique=True)

    class Meta:
        verbose_name_plural = "标签表"

    def __str__(self):
        return self.name


class IDC(models.Model):
    """
    机房信息
    """
    name = models.CharField('机房', max_length=32)
    floor = models.IntegerField('楼层', default=1)

    class Meta:
        verbose_name_plural = "05机房表"

    def __str__(self):
        return self.name


class Server(models.Model):
    """
    服务器信息
    """
    # asset = models.OneToOneField('Asset')

    idc = models.ForeignKey(IDC, verbose_name="IDC", null=True, blank=True)
    cabinet_num = models.CharField('机柜号', max_length=30, null=True, blank=True)
    cabinet_order = models.CharField('机柜中序号', max_length=30, null=True, blank=True)

    business_unit = models.ForeignKey(BusinessUnit, verbose_name="业务线(部门)", null=True, blank=True)

    tags = models.ManyToManyField(Tag)

    server_status_choices = (
        (1, '上架'),
        (2, '在线'),
        (3, '离线'),
        (4, '下架'),
    )

    server_status_id = models.IntegerField(choices=server_status_choices, default=1)

    hostname = models.CharField(max_length=128, unique=True)
    sn = models.CharField(verbose_name='SN号', max_length=128, db_index=True)
    manufacturer = models.CharField(verbose_name='制造商', max_length=64, null=True, blank=True)
    model = models.CharField(verbose_name='型号', max_length=64, null=True, blank=True)

    manage_ip = models.GenericIPAddressField(verbose_name='管理IP', null=True, blank=True)

    os_platform = models.CharField(verbose_name='系统', max_length=16, null=True, blank=True)
    os_version = models.CharField(verbose_name='系统版本', max_length=128, null=True, blank=True)

    cpu_count = models.IntegerField(verbose_name='CPU个数', null=True, blank=True)
    cpu_physical_count = models.IntegerField(verbose_name='CPU物理个数', null=True, blank=True)
    cpu_model = models.CharField(verbose_name='CPU型号', max_length=128, null=True, blank=True)

    create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, blank=True)

    latest_date = models.DateTimeField(verbose_name="最后修改时间", null=True, blank=True)

    class Meta:
        verbose_name_plural = "06服务器表"

    def __str__(self):
        return self.hostname


class Disk(models.Model):
    """
    硬盘信息
    """
    slot = models.CharField('插槽位', max_length=8)
    model = models.CharField('磁盘型号', max_length=128)
    capacity = models.FloatField('磁盘容量GB')
    pd_type = models.CharField('磁盘类型', max_length=32)
    server_obj = models.ForeignKey('Server', related_name='disk', verbose_name="主机名")

    class Meta:
        verbose_name_plural = "07硬盘表"

    def __str__(self):
        return "%s-%s-%s" % (self.server_obj, self.slot, self.model)


class NIC(models.Model):
    """
    网卡信息
    """
    name = models.CharField('网卡名称', max_length=128)
    hwaddr = models.CharField('网卡mac地址', max_length=64)
    netmask = models.CharField(max_length=64)
    ipaddrs = models.CharField('ip地址', max_length=256)
    up = models.BooleanField(default=False)
    server_obj = models.ForeignKey('Server', related_name='nic', verbose_name="主机名")

    class Meta:
        verbose_name_plural = "06网卡表"

    def __str__(self):
        return "%s-%s-%s" % (self.server_obj, self.name, self.ipaddrs)


class Memory(models.Model):
    """
    内存信息
    """
    slot = models.CharField('插槽位', max_length=32)
    manufacturer = models.CharField('制造商', max_length=32, null=True, blank=True)
    model = models.CharField('型号', max_length=64)
    capacity = models.FloatField('容量', null=True, blank=True)
    sn = models.CharField('内存SN号', max_length=64, null=True, blank=True)
    speed = models.CharField('速度', max_length=16, null=True, blank=True)

    server_obj = models.ForeignKey('Server', related_name='memory', verbose_name="主机名")

    class Meta:
        verbose_name_plural = "08内存表"

    def __str__(self):
        return "%s-%s-%s" % (self.server_obj, self.slot, self.manufacturer)


class ServerRecord(models.Model):
    """
    服务器变更记录,creator为空时，表示是资产汇报的数据。
    """
    server_obj = models.ForeignKey('Server', related_name='ar')
    content = models.TextField(null=True)
    creator = models.ForeignKey('UserProfile', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "资产记录表"

    def __str__(self):
        return self.server_obj.hostname


class ErrorLog(models.Model):
    """
    错误日志,如：agent采集数据错误 或 运行错误
    """
    server_obj = models.ForeignKey('Server', null=True, blank=True)
    title = models.CharField(max_length=16)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "07错误日志表"

    def __str__(self):
        return self.title


class SelfConfig(models.Model):
    """
    自用配置文件
    """
    title = models.CharField(verbose_name="配置名称", max_length=64)
    allocation = models.TextField(verbose_name="对应配置", null=True, help_text='例如：证书key-crt-url-字典形式存放')
    notes = models.TextField(verbose_name="备注", )
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "08自用配置文件"

    def __str__(self):
        return self.title


class Configcenter(models.Model):
    """
    配置文件内容
    """
    publish_choices = (
        (1, '发布'),
        (2, '不发布'),
    )
    publish_id = models.IntegerField(verbose_name='是否发布', choices=publish_choices, default=2)  # 是否发布
    title = models.CharField(verbose_name="配置名", max_length=64)
    content = models.TextField(verbose_name="配置内容", )
    notes = models.TextField(verbose_name="备注", )

    conftype_choices = (
        (1, '未配置'),
        (2, 'configmaps'),
        (3, 'ingresses'),
    )
    conftype_id = models.IntegerField(verbose_name='配置文件类型', choices=conftype_choices, default=1)  # 配置类型

    create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    latest_date = models.DateTimeField(verbose_name="修改时间", null=True, auto_now=True)
    publish_status_choices = (
        (1, '存活'),
        (2, '失效'),
    )
    publish_status_id = models.IntegerField(verbose_name='配置文件状态', choices=publish_status_choices, default=1)  # 状态

    change_user = models.ForeignKey('UserProfile', null=True, blank=True, verbose_name="修改人")  # 修改人
    environment_choices = (
        (1, '正式'),
        (2, '测试'),
    )
    environment_id = models.IntegerField(verbose_name='当前环境', choices=environment_choices, default=1)  # 配置属于哪个环境
    configrelation = models.ManyToManyField('SelfConfig', verbose_name='关联操作')

    class Meta:
        verbose_name_plural = "09configmap配置文件内容"

    def __str__(self):
        return self.title


class Resourcecontroller(models.Model):
    """
    kubernetes资源控制器
    """
    publish_choices = (
        (1, '发布'),
        (2, '不发布'),
    )
    publish_id = models.IntegerField(verbose_name='是否发布', choices=publish_choices, default=2)  # 是否发布
    title = models.CharField(verbose_name="配置名", max_length=64)
    content = models.TextField(verbose_name="配置内容", )
    notes = models.TextField(verbose_name="备注", )

    conftype_choices = (
        (1, '未配置'),
        (2, 'daemonsets'),
        (3, 'deployments'),
        (4, 'statefulsets'),
    )
    conftype_id = models.IntegerField(verbose_name='配置文件类型', choices=conftype_choices, default=1)  # 配置类型

    create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    latest_date = models.DateTimeField(verbose_name="修改时间", null=True, auto_now=True)
    publish_status_choices = (
        (1, '存活'),
        (2, '失效'),
    )
    publish_status_id = models.IntegerField(verbose_name='配置文件状态', choices=publish_status_choices, default=1)  # 发布状态
    change_user = models.ForeignKey('UserProfile', null=True, blank=True, verbose_name="修改人")  # 修改人
    environment_choices = (
        (1, '正式'),
        (2, '测试'),
    )
    environment_id = models.IntegerField(verbose_name='当前环境', choices=environment_choices, default=2)  # 配置属于哪个环境
    configrelation = models.ManyToManyField('SelfConfig', verbose_name='关联操作')  # 关联自己配置文件，该配置文件，在脚本中执行时，会对哪些环境重启
    configmaprelation = models.ManyToManyField('Configcenter',
                                               verbose_name='关联configmap')  # 与哪些configmap关联，如果configmap修改，方便关联重启

    class Meta:
        verbose_name_plural = "10控制器配置文件内容"

    def __str__(self):
        return self.title


class Host(models.Model):
    hostname = models.CharField(db_index=True, max_length=60, null=False, verbose_name='主机名')
    i_ip = models.CharField(max_length=30, null=False, verbose_name='内网IP')
    o_ip = models.CharField(max_length=30, null=False, verbose_name='外网IP')
    cpu_info = models.CharField(max_length=30, verbose_name='CPU')
    mem_info = models.CharField(max_length=30, verbose_name='内存')
    disk_info = models.CharField(max_length=30, verbose_name='磁盘')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    host_status_choices = (
        (0, '失效'),
        (1, '存活'),
    )
    status = models.IntegerField(choices=host_status_choices, null=True, verbose_name='主机状态')
    remarks = models.CharField(max_length=200, null=True, verbose_name='备注')
    instanceid = models.CharField(max_length=30, null=True, verbose_name='标识')

