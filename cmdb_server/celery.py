# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     celery
   Description :
   Author :       admin
   date：          2018-12-10
-------------------------------------------------
   Change Activity:
                   2018-12-10:

-------------------------------------------------
"""
from __future__ import absolute_import, unicode_literals # 必须发生在文件的开头
__author__ = 'admin_Fred'
import os
from celery import Celery

# 为“celery”程序设置默认的Django设置模块。
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmdb_server.settings')  # 填写配置文件目录+配置文件名

# 可以不需要这个配置，作用是避免将配置文件目录（模块）传递给celery程序。配置必须总是在创建应用程序实例之前出现
app = Celery('cmdb_server')



'''
这是我们的库实例，您可以有很多实例，但是在使用Django时可能没有理由这样做。
我们还添加Django设置模块作为 selery 的配置源。这意味着您不必使用多个配置文件，'
而是直接从Django设置中配置 selery;但你也可以把它们分开。
大写的名称空间意味着所有 selery 配置选项必须以大写而不是小写指定，
并以 CELERY_ 开头，例如: setting: 'task_always_eager' 设置变成 CELERY_BROKER_URL，
而:setting:'broker_url' 设置变成CELERY_BROKER_URL。
您可以在这里直接传递对象，但是使用字符串更好，因为 worker 工作 不必序列化对象。
'''
# 在这里使用字符串意味着 worker 不必序列化
# 子进程的配置对象
# - namespace='CELERY' 表示所有与快速相关的配置键
#   #应该有一个' CELERY_ '前缀。
app.config_from_object('django.conf:settings', namespace='CELERY')  # 指定celery 配置文件路径， 我们将相关配置放入了django中得settinggs

# 从所有注册的Django app(应用) configs加载任务模块。
# 接下来，可重用应用程序的常见实践是在单独的任务中定义所有任务。
# py模块和celery确实有一种自动发现这些模块的方法:

app.autodiscover_tasks()

