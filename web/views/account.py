#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render, HttpResponse, redirect
from rbac import models as rbac_model
from repository import models as repository_models
from rbac.service.init_permission import init_permission


def login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')

    user = request.POST.get('user')
    pwd = request.POST.get('pwd')

    # 根据用户名和密码去用户表中获取用户对象
    # user = rbac_model.UserInfo.objects.filter(name=user, password=pwd).first()
    user = repository_models.AdminInfo.objects.filter(username=user, password=pwd).first()

    if not user:
        return render(request, 'login.html', {'msg': '用户名或密码错误'})

    init_permission(user, request)
    return redirect('/user/info/')


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.delete()

    return redirect('/login/')
