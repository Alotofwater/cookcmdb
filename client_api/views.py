import json
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from repository import models
from .plugins import PluginManger
from django.db.models import Q
from datetime import date
import hashlib
import time


@csrf_exempt  # 不走csrf验证
def server(request):
    if request.method == "GET":  # 页面数据展示
        # GET请求返回数据
        current_date = date.today()
        # 获取今日未采集的主机列表
        host_list = models.Server.objects.filter(
            Q(Q(latest_date=None) | Q(latest_date__date__lt=current_date)) & Q(server_status_id=2)
        ).values('hostname')
        host_list = list(host_list)
        return HttpResponse(json.dumps(host_list))

    elif request.method == "POST":
        # 客户端提交的最新资产数据
        server_dict = json.loads(request.body.decode('utf-8'))  # 反序列化-获取client端提交数据
        print("server_dict_view:::::",server_dict)
        # 检查server表中是否有当前资产信息【主机名是唯一标识】
        if not server_dict['basic']['status']:  # 查看状态
            return HttpResponse('服务器状态不对')

        manager = PluginManger()  # 插件管理员实例化
        response = manager.exec(server_dict)  # 获取的数据，写入数据库中

        return HttpResponse(json.dumps(response))


# ############################################## API验证示例 ##############################################
def md5(arg):
    hs = hashlib.md5()
    hs.update(arg.encode('utf-8'))
    return hs.hexdigest()


key = "asdfuasodijfoausfnasdf"
# redis,Memcache
visited_keys = {
    # "841770f74ef3b7867d90be37c5b4adfc":时间,  10
}


def api_auth(func):
    def inner(request, *args, **kwargs):
        server_float_ctime = time.time()
        auth_header_val = request.META.get('HTTP_AUTH_API')
        # 841770f74ef3b7867d90be37c5b4adfc|1506571253.9937866
        client_md5_str, client_ctime = auth_header_val.split('|', maxsplit=1)
        client_float_ctime = float(client_ctime)

        # 第一关
        if (client_float_ctime + 20) < server_float_ctime:
            return HttpResponse('时间太久了，再去买一个吧')

        # 第二关：
        server_md5_str = md5("%s|%s" % (key, client_ctime,))
        if server_md5_str != client_md5_str:
            return HttpResponse('休想')

        # 第三关：
        if visited_keys.get(client_md5_str):
            return HttpResponse('你放弃吧，来晚了')

        visited_keys[client_md5_str] = client_float_ctime
        return func(request, *args, **kwargs)

    return inner


@api_auth
def test(request):
    return HttpResponse('正常用户')


def tran(request):
    from django.db import transaction
    try:
        with transaction.atomic():
            models.UserProfile.objects.create(name='a1', email='xxx', phone='xxxx', mobile='xxxx')
            models.Server.objects.create(hostname='uuuuu', sn='FDIJNFIK234')
    except Exception as e:
        return HttpResponse('出现错误')

    return HttpResponse('执行成功')
