# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    rdslistapi
   Description :
   Author :       fred
   date：         2019-01-09
-------------------------------------------------
   Change Activity:
                  2019-01-09:
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
from django.contrib.sessions import models as sessionmodels  # session表
from rest_framework.parsers import JSONParser  # Content-Type 数据类型
# 自己
from mrest_api.serializers_list.rdslist import RdsListModelSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    page_query_param = 'p'
    max_page_size = 100


class RdslistView(ViewSetMixin, APIView):
    parser_classes = [JSONParser]  # 只允许 Content-Type: application/json 数据类型

    def get(self, request, *args, **kwargs):
        # response = {'code':1000,'data':None,'error':None}
        ret = BaseResponse()
        if request.version == 'v1':

            try:
                print('request.version', request.version)
                # 从数据库获取数据
                queryset = models.Rdslist.objects.all()
                print('queryset', queryset)
                # 分页
                page = StandardResultsSetPagination()

                rds_list = page.paginate_queryset(queryset, request, self)
                print('rds_list', rds_list)
                # 分页之后的结果执行序列化
                ser = RdsListModelSerializer(instance=rds_list, many=True)

                ret.data = ser.data
            except Exception as error:
                print("get-error", error)
                ret.code = 500
                ret.error = '获取数据失败'
            return JsonResponse(ret.dict)

    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        if request.version == 'v1':
            try:

                postdata = self.request.data
                print('postdata', postdata)
                authkey = postdata.get("auth")
                sessionobj = sessionmodels.Session.objects.filter(session_key=authkey).first()
                if not sessionobj:
                    ret.code = 20050
                    ret.error = '你未登陆系统'
                    return JsonResponse(ret.dict)
                # 如果不是列表数据格式，直接退出

                if not isinstance(postdata, dict):
                    ret.code = 50002
                    ret.error = 'post提交数据类型不正确'
                    return JsonResponse(ret.dict)

                craeterdsdict = []
                for rdsdict in postdata.get("postdata"):  # type:dict
                    # 判断提交的key数据是否正常
                    keyjudge = ['DBInstanceDescription', 'DBInstanceId', 'ConnectionString', 'InstancenetWorkType', 'Engine', 'EngineVersion']
                    for k in keyjudge:
                        if not k in rdsdict:
                            ret.code = 50002
                            ret.error = 'post提交数据参数 %s 不存在' % (k)
                            return JsonResponse(ret.dict)

                    DBInstanceIdjudge = rdsdict.get('DBInstanceId')

                    print('DBInstanceIdjudge', DBInstanceIdjudge)
                    rdsjudge = models.Rdslist.objects.filter(DBInstanceId=DBInstanceIdjudge)
                    print('rdsjudge', rdsjudge)
                    if not rdsjudge:
                        # 打散 添加 待插入列表中
                        craeterdsdict.append(models.Rdslist(**rdsdict))

                # 判断需要写入的列表是否未空
                print('craeterdsdict', craeterdsdict)
                if not craeterdsdict:
                    ret.code = 20002
                    ret.data = '没有需要创建的新数据'
                    return JsonResponse(ret.dict)

                # 批量写入数据

                models.Rdslist.objects.bulk_create(craeterdsdict)

                ret.data = "rds录入成功%s" % (craeterdsdict)
                ret.code = "20000"
            except Exception as error:
                print("post-error", error)
                ret.error = error
                ret.data = "rds录入失败"
                ret.code = "5000"
            return JsonResponse(ret.dict)

    def put(self, request, *args, **kwargs):  # 修改
        pass

    def delete(self, request, *args, **kwargs):  # 删除
        pass
