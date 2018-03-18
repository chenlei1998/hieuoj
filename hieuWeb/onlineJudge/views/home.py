# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.views.generic import View

from onlineJudge.models import Category, ProblemJudgeTask, Problem


class HomeView(View):
    def get(self, request):
        title = request.GET.get('category') or 'ALL'
        page = request.GET.get('page') or 1
        page = int(page)
        if page <= 0:
            return redirect('error:404')
        try:
            if 'ALL' == title:
                problems = Problem.objects.order_by('id').filter(
                    pk__in=Category.problems.through.objects.values("problem").distinct())
            else:
                category = Category.objects.get(title=title)
                problems = Problem.objects.order_by('id').filter(pk__in=Category.problems.through.objects.values("problem").filter(category=category).distinct())

            for problem in problems:
                problem.total_submit = ProblemJudgeTask.objects.filter(Q(problem_id=problem.id)).count()
                problem.total_ac = ProblemJudgeTask.objects.filter(Q(problem_id=problem.id) & Q(status='ACCEPTED')).count()

            paginator = Paginator(problems, 20)
            total_page = 10
            before_pages = [i for i in xrange(page - total_page / 2, page) if i >= 1]
            after_pages = [i for i in xrange(page + 1, page + total_page - len(before_pages)) if
                           i <= paginator.num_pages]
            context = {
                'problems':
                    paginator.page(page),
                'category_list':
                    Category.objects.values('title').annotate(count=Count("problems__id")),
                'total_num':
                    Category.objects.values('problems').distinct().aggregate(count=Count("problems__id"))['count'],
                'current_category':
                    title,
                'before_pages':
                    before_pages,
                'after_pages':
                    after_pages
            }
            return render(request, 'home.html', context)
        except InvalidPage:
            return redirect('error:404')
        except Category.DoesNotExist:
            return redirect('error:404')
