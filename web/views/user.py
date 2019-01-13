#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render


def info(request):
    cc = request.session.session_key
    print('info',cc)
    return render(request, 'info.html')
