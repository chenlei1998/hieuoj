# -*- coding: utf-8 -*-
from django.views.generic import View
from django.shortcuts import render
from onlineJudge.models import Category, Problem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class HomeWorkView(View):
    def get(self, request):
        title = request.GET.get('category')
        page = request.GET.get('page')
        try:
            category = Category.objects.get(title=title)
            print type(category)
            return render('home.html')
        except:
            pass