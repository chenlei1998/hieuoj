# -*- coding: utf-8 -*-
from django.shortcuts import render


def error_404(request):
    return render(request, '404.html')


def get_urls():
    from django.conf.urls import url
    urlpatterns = [
        url(r'^404.html/$', error_404, name='404'),
    ]
    return urlpatterns, 'onlineJudge', 'error'
