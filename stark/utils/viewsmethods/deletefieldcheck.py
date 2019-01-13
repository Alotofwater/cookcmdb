# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    deletefieldcheck
   Description :
   Author :       fred
   date：         2019-01-04
-------------------------------------------------
   Change Activity:
                  2019-01-04:
-------------------------------------------------
"""
from django.shortcuts import render

import logging

logger = logging.getLogger('django_default')


def DeleteFieldCheck(func):
    def wrapper(self, request, pk, *args, **kwargs):

        # 判断数据结果 如果 False 说明字段 验证不通过
        fieldjudgedict = {}
        # 获取对象本身 删除 数据的条件  deletefieldcheckjudge 应用了stark 组件 填写配置
        deletefieldcheckdata = self.deletefieldcheckjudge  # type:dict

        if deletefieldcheckdata:
            ormobj = self.model_class.objects.filter(pk=pk).first()

            for key in deletefieldcheckdata.keys():
                value = str(deletefieldcheckdata.get(key))
                keyfieldjudge = str(getattr(ormobj, key))
                logger.debug("verbose_name:%s value:%s" % (ormobj._meta.get_field(key).verbose_name, getattr(ormobj,"get_%s_display" % key)()))
                if not value == keyfieldjudge:
                    #  说明字段 验证不通过
                    fieldjudgedict[key] = {'status':False,
                                           "fieldname":ormobj._meta.get_field(key).verbose_name,
                                           "fieldvalue":getattr(ormobj,"get_%s_display" % key)()
                                           }

                if value == keyfieldjudge:
                    fieldjudgedict[key] = True
            # 校验
            for k,v in fieldjudgedict.items():
                if v.get("status") == False:
                    logger.debug("fieldjudgedict:%s 'status':False" %(fieldjudgedict))
                    return render(request, 'stark/delete.html', {'cancel_url': self.reverse_list_url(),
                                                                 "fieldjudgedict":fieldjudgedict.get(k) # 只获取状态数据
                                                                 })

        ret = func(self, request, pk, *args, **kwargs)
        logger.debug("fieldjudgedict:%s 'status':True" % (fieldjudgedict))
        return ret

    return wrapper
