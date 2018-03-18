# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import View


class MyContest(View):
    def get(self, request):
        return render(request, 'widgets/my_contest.html')


class SystemInfo(View):
    def get(self, request):
        return render(request, 'widgets/system_info.html')


class MySubmit(View):
    def get(self, request):
        return render(request, 'widgets/my_submit.html')
