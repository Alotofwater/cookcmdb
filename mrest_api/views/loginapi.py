# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    loginapi
   Description :
   Author :       fred
   date：         2019-01-10
-------------------------------------------------
   Change Activity:
                  2019-01-10:
-------------------------------------------------
"""
from rest_framework.viewsets import ViewSetMixin  # ViewSetMixin 是给  as_view({'get':'list','post':'create'})
from repository import models
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView  #
from utils.common.response import BaseResponse
from rest_framework.response import Response

# django
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from repository import models as repository_models



from rbac.service.init_permission import init_permission

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser  # Content-Type 数据类型


from django.contrib.sessions import models as sessionmodels  # session表



# 自己
from mrest_api.serializers_list.rdslist import RdsListModelSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    page_query_param = 'p'
    max_page_size = 100


class LoginlistView(ViewSetMixin, APIView):
    parser_classes = [JSONParser]  # 只允许 Content-Type: application/json 数据类型

    def get(self, request, *args, **kwargs):

        # response = {'code':1000,'data':None,'error':None}
        ret = BaseResponse()
        if request.version == 'v1':
            try:
                sessionobj = sessionmodels.Session.objects.filter(session_key=request.session.session_key).first()

                ret.data = {'test':'get','sessionkey':sessionobj.session_key,'expire_date':sessionobj.expire_date}
            except Exception as error:
                print("get-error", error)
                ret.code = 500
                ret.error = '获取数据失败'
            return JsonResponse(ret.dict)
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        if request.version == 'v1':
            try:
                username = request.data.get("username")
                passwd = request.data.get("passwd")
                user = repository_models.AdminInfo.objects.filter(username=username, password=passwd).first()

                if not user:
                    ret.data = "用户名或密码错误"
                    return JsonResponse(ret.dict)
                # 获取权限
                init_permission(user, request._request)

                ret.data = {'session_key':request.session.session_key,'conn':'登陆成功'}
                ret.code = "20000"
            except Exception as error:
                print("post-error", error)
                ret.error = error
                ret.data = "rds录入失败"
                ret.code = "5000"
            return JsonResponse(ret.dict)