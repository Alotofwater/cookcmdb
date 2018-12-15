
from django.conf.urls import url, include
from client_api import views

urlpatterns = [
    url(r'^server$', views.server,name="server"), # api提交地址  # 设置name="server"，别名所有 url都要设置
    # url(r'^test.html$', views.test,name="test.html"), # 测试
    # url(r'^tran.html$', views.tran,name="tran.html"),
]

