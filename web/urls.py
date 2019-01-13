from django.conf.urls import url
from web.views import account
# from web.views import customer
# from web.views import payment
from web.views import user

urlpatterns = [

    url(r'^user/info/$', user.info, name='user_info'),
    url(r'^login/$', account.login, name='login'),
    url(r'^logout/$', account.logout, name='logout'),

]
