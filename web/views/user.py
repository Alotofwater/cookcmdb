#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render


def info(request):
    return render(request, 'info.html')
