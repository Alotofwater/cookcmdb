from __future__ import absolute_import, unicode_literals # 必须发生在文件的开头

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

from .celery import app as celery_app
'''
这将确保应用程序总是在导入时
# Django启动，shared_task将使用这个应用程序。
'''
__all__ = ['celery_app']