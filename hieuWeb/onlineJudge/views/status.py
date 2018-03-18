# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.conf import settings

from onlineJudge.models import ProblemJudgeTask, StudentProfile


class StatusView(View):
    def get(self, request):
        page = request.GET.get('page') or 1
        page = int(page)
        q = Q()
        filter_form_data = dict()
        if 'username' in request.GET and request.GET['username'].strip():
            filter_form_data['username'] = request.GET['username'].strip()
            q = Q(user__username=request.GET['username'].strip())
        if 'problem_id' in request.GET and request.GET['problem_id'].strip():
            filter_form_data['problem_id'] = request.GET['problem_id'].strip()
            q &= Q(problem_id=int(request.GET['problem_id'].strip()))
        if 'status' in request.GET and request.GET['status'].strip():
            filter_form_data['status'] = request.GET['status'].strip()
            q &= Q(status=request.GET['status'].strip())
        if 'department' in request.GET and request.GET['department'].strip():
            filter_form_data['department'] = request.GET['department'].strip()
            q &= Q(user__studentprofile__department=request.GET['department'].strip())
        if 'class' in request.GET and request.GET['class'].strip():
            filter_form_data['class'] = request.GET['class'].strip()
            q &= Q(user__studentprofile___class=request.GET['class'].strip())

        try:
            paginator = Paginator(ProblemJudgeTask.objects.filter(q).order_by('-pub_date'), 20)
            total_page = 10
            before_pages = [i for i in xrange(page - total_page / 2, page) if i >= 1]
            after_pages = [i for i in xrange(page + 1, page + total_page - len(before_pages)) if
                           i <= paginator.num_pages]
            context = {
                'task_list': paginator.page(page),
                'before_pages':
                    before_pages,
                'after_pages':
                    after_pages,
                'department_list':
                    StudentProfile.objects.all().values('department').distinct(),
                'filter_form_data':
                    filter_form_data,
                'status_list':
                    [getattr(settings, attr_name) for attr_name in 'AC CE WA SE RE PE MLE TLE RTLE OLE'.split()]
            }
            return render(request, 'status.html', context)
        except InvalidPage:
            return redirect('error:404')


