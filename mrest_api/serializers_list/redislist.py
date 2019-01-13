# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    rdslist
   Description :
   Author :       fred
   date：         2019-01-09
-------------------------------------------------
   Change Activity:
                  2019-01-09:
-------------------------------------------------
"""


from rest_framework import serializers
from repository import models
class RedisListModelSerializer(serializers.ModelSerializer):
    '''
    查看所有学位课并打印学位课名称以及授课老师
    '''
    rdslist = serializers.SerializerMethodField()
    class Meta:
        model = models.Redislist
        fields = "__all__"

    def get_rdslist(self,rowobj):
        # teachers_list = rowobj.teachers.all()
        # print('teachers_list',teachers_list)
        return [222,333,444,222]
        # return [ {"id":itme.pk,"name":itme.name} for itme in teachers_list]
