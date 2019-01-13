from django.db import models


class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(verbose_name='菜单', max_length=32)
    icon = models.CharField(verbose_name='图标', max_length=32)

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的URL', max_length=128, unique=True)

    name = models.CharField(verbose_name='代码', max_length=64, unique=True, null=False, blank=False)

    pid = models.ForeignKey(verbose_name='默认选中权限', to='Permission', related_name='ps', null=True, blank=True,
                            help_text="对于无法作为菜单的URL，可以为其选择一个可以作为菜单的权限，那么访问时，则默认选中此权限",
                            limit_choices_to={'menu__isnull': False}, on_delete=models.SET_NULL)

    menu = models.ForeignKey(verbose_name='菜单', to='Menu', null=True, blank=True, help_text='null表示非菜单',
                             on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色
    """
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)

    def __str__(self):
        return self.title


# class UserInfo(models.Model):
#     """
#     用户表
#     """
#     name = models.CharField(verbose_name='用户名', max_length=32)
#     password = models.CharField(verbose_name='密码', max_length=64)
#     email = models.CharField(verbose_name='邮箱', max_length=32)
#     roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role', blank=True)
#
#     def __str__(self):
#         return self.name

class UserInfo(models.Model):
    """
    用户表
    """
    # name = models.CharField(verbose_name='用户名', max_length=32)
    # password = models.CharField(verbose_name='密码', max_length=64)
    # email = models.CharField(verbose_name='邮箱', max_length=32)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to=Role, blank=True)

    class Meta:
        verbose_name_plural = "03.用户表"
        abstract = True