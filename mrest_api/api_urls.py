from django.conf.urls import url
from mrest_api.views import rdslistapi
from mrest_api.views import redislistapi
from mrest_api.views import loginapi

urlpatterns = [

    url(r'^rdsapi/$', rdslistapi.RdslistView.as_view({'get': 'get', 'post': 'post'}), name='getpostrdsapi'),  # 阿里云rds
    url(r'^rdsapi/(?P<pk>\d+)/$', rdslistapi.RdslistView.as_view({'put': 'put', 'delete': 'delete'}), name='putdeleterdsapi'),# 阿里云rds

    url(r'^redisapi/$', redislistapi.RedislistView.as_view({'get': 'get', 'post': 'post'}), name='getpostredisapi'),  # 阿里云redis
    url(r'^redisapi/(?P<pk>\d+)/$', redislistapi.RedislistView.as_view({'put': 'put', 'delete': 'delete'}),name='putdeleteredisapi'),  # 阿里云redis

    url(r'^loginapi/$', loginapi.LoginlistView.as_view({'get': 'get', 'post': 'post'}), name='getpostloginapi'),
]

# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'course_detail', views.Course_detail)
# urlpatterns += router.urls
