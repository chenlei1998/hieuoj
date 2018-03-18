# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views import View
from django.shortcuts import render, redirect
from django.db.models import Count, Prefetch, When, F, Q
from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage

from onlineJudge.models import ProblemJudgeTask, UserRankList


class RankListView(View):
    def get(self, request):
        page = request.GET.get('page') or 1
        page = int(page)
        try:
            ranklist =  (UserRankList.objects.filter(user__is_staff=False)
                        .extra(select={'pass_ratio': 'ROUND((1.0 * ac_submit)/total_submit * 100, 2)'})
                         .select_related('user')
                         .order_by('-solved_count'))

            paginator = Paginator(ranklist, 20)
            total_page = 10
            before_pages = [i for i in xrange(page - total_page / 2, page) if i >= 1]
            after_pages = [i for i in xrange(page + 1, page + total_page - len(before_pages)) if
                           i <= paginator.num_pages]
            context = {
                'ranklist': paginator.page(page),
                'before_pages':
                    before_pages,
                'after_pages':
                    after_pages
            }
            return render(request, 'ranklist.html', context)
        except InvalidPage:
            return redirect('error:404')


def get_urls():
    urlpatterns = [
        url(r'^$', RankListView.as_view(), name='index'),
    ]
    return urlpatterns, 'onlineJudge', 'ranklist'