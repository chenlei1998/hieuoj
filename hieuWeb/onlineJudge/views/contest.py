# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.views.generic import View
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth.models import User
from onlineJudge.models import Contest, ContestJudgeTask
from onlineJudge.forms import SolutionForm
from onlineJudge.utils import submit_task, problems_to_ab_map

from collections import defaultdict
from datetime import timedelta

class ContestView(View):
    def get(self, request):
        contest_type = request.GET.get('type') or 'all'
        page = request.GET.get('page') or 1
        page = int(page)
        if page <= 0:
            return redirect('error:404')
        if contest_type == 'all':
            contest_list = Contest.objects.order_by('-start_date').all()
        elif contest_type == 'pending':
            contest_list = Contest.objects.filter(start_date__gt=timezone.now())
        elif contest_type == 'finish':
            contest_list = Contest.objects.filter(end_date__lt=timezone.now())
        else:
            return redirect('404error')

        try:
            paginator = Paginator(contest_list, 20)
            total_page = 10
            before_pages = [i for i in xrange(page - total_page / 2, page) if i >= 1]
            after_pages = [i for i in xrange(page + 1, page + total_page - len(before_pages)) if i <= paginator.num_pages]
            context = {
                'before_pages':
                    before_pages,
                'after_pages':
                    after_pages,
                'contest_type':
                    contest_type,
                'contest_list':
                    paginator.page(page),
                'page':
                    page
            }
            return render(request, 'contest/index.html', context)
        except InvalidPage:
            return redirect('error:404')


class ContestDetailsView(View):
    def get(self, request, id):
        page = request.GET.get('page') or 1
        page = int(page)
        try:
            contest = Contest.objects.get(id=id)
            problems = contest.problems.all().order_by('id')
            ab_mapping = problems_to_ab_map(problems)
            ac_users = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

            class Rank(object):
                def __init__(self):
                    self.user = None
                    # 解题消耗的总时间
                    self.total_time = timedelta()
                    self.items = []

                @property
                def total_solution(self):
                    return len(self.solution_set)

            # 获取所有参赛用户
            user_list = ContestJudgeTask.objects.filter(contest=contest).values('user_id').distinct()

            rank_list = {}
            for user in user_list:
                items = []
                for problem in problems:
                    # 用户在当前问题上的状态
                    problem_status = {
                        'punish': timedelta(),
                        'cost': timedelta
                    }
                    # 获取用户的所有提交
                    solution_list = ContestJudgeTask.objects.filter(contest=contest, problem_id=problem.id, user_id=user['user_id']).order_by('pub_date')
                    ac_flag = False
                    for solution in solution_list:
                        if solution.status == 'ACCEPTED':
                            # 取第一次AC的提交
                            if ac_flag is False:
                                # 解题耗时
                                problem_status['cost'] = solution.pub_date - contest.start_date
                                ac_flag = True

                        elif solution.status not in ['RUNNING', 'PENDING']:
                            # 在此问题上的罚时
                            problem_status['punish'] += timedelta(minutes=20)
                    problem_status['id'] = ab_mapping[problem.id]
                    problem_status['ac'] = ac_flag
                    items.append(problem_status)
                items = sorted(items, key=lambda x:x['id'])
                rank_list[user['user_id']] = {'items': items, 'ac_count': len([item for item in items if item['ac']])}
            rank_list = rank_list.items()

            def rank_cmp(item_a, item_b):
                if item_a['ac_count'] == item_b['ac_count']:
                    total_time_a = timedelta()
                    total_time_b = timedelta()
                    for item in item_a['items']:
                        if item['ac']:
                            total_time_a += item['cost']
                            total_time_a += item['punish']
                    for item in item_b['items']:
                        if item['ac']:
                            total_time_b += item['cost']
                            total_time_b += item['punish']
                    return cmp(total_time_b, total_time_a)
                else:
                    return cmp(item_a['ac_count'], item_b['ac_count'])
            rank_list = [(User.objects.get(id=uid), item) for uid, item in sorted(rank_list, cmp=rank_cmp, key=lambda x: x[1], reverse=True)]

            paginator = Paginator(contest.contestjudgetask_set.all().order_by('-pub_date'), 10)
            total_page = 10
            before_pages = [i for i in xrange(page - total_page / 2, page) if i >= 1]
            after_pages = [i for i in xrange(page + 1, page + total_page - len(before_pages)) if
                           i <= paginator.num_pages]
            task_list = paginator.page(page)
            for task in task_list:
                task.slug = ab_mapping[task.problem_id]

            context = {
                'rank_list': rank_list,
                'contest':
                    contest,
                'problems':
                    [(ab_mapping[problem.id], problem) for problem in problems],
                'after_pages':
                    after_pages,
                'before_pages':
                    before_pages,
                'current_page':
                    page,
                'task_list':
                    task_list
            }

            for problem in problems:
                problem.total_submit = ContestJudgeTask.objects.filter(problem_id=problem.id).count()
                problem.total_ac = ContestJudgeTask.objects.filter(Q(problem_id=problem.id) & Q(status='ACCEPTED')).count()

            if contest.status() == 'pending':
                return redirect('error:404')
            return render(request, 'contest/details.html', context)
        except Contest.DoesNotExist:
            return redirect('error:404')
        except InvalidPage:
            return redirect('error:404')


class ContestProblemView(View):
    def get(self, request, contest_id, problem_id):
        try:
            contest = Contest.objects.get(id=contest_id)
            if timezone.now() > contest.end_date:
                return redirect('contest:details', contest_id)
            ab_mapping = dict([(v, k) for k, v in problems_to_ab_map(contest.problems.all()).items()])
            problem = contest.problems.all().get(id=ab_mapping[problem_id])
            context = {
                'problem':
                    problem,
            }
            return render(request, 'problem.html', context)
        except ObjectDoesNotExist:
            return redirect('error:404')

    def post(self, request, contest_id, problem_id):
        try:
            solution_form = SolutionForm(request.POST)
            if request.user.is_authenticated() is False:
                return JsonResponse({'status': 'unlogin'})
            elif solution_form.is_valid():
                contest = Contest.objects.get(id=contest_id)
                if timezone.now() > contest.end_date:
                    return JsonResponse({'status': 'error', 'error_msg':u'比赛已结束'})
                ab_mapping = dict([(v, k) for k, v in problems_to_ab_map(contest.problems.all()).items()])
                problem = contest.problems.all().get(id=ab_mapping[problem_id])
                task = ContestJudgeTask(problem=problem,
                                        contest=contest,
                                        user=request.user,
                                        lang=solution_form.cleaned_data['lang'],
                                        code=solution_form.cleaned_data['code'],
                                        status=u'PENDING')
                task.save()
                submit_task(task.task_id, task.lang, task.code, problem.input, problem.output,
                            problem.memory_limit, problem.time_limit, reverse('contest:report-status'))
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({'status': 'error', 'errors': dict([(k, v[0]) for k, v in solution_form.errors.items()])})
        except ObjectDoesNotExist:
            return redirect('error:404')


def report_task_status(request):
    task_id = request.GET.get('task_id')
    used_time = request.GET.get('used_time') or 0
    used_memory = request.GET.get('used_memory') or 0
    status = request.GET.get('status')
    try:
        task = ContestJudgeTask.objects.get(task_id=task_id)
        task.status = status
        task.used_time = float(used_time)
        task.used_memory = float(used_memory)
        task.save()
        #print task.status
        return JsonResponse({'status': 'success'})
    except ContestJudgeTask.DoesNotExist:
        return redirect('error:404')


def get_urls():
    from django.conf.urls import url
    urlpatterns = [
        url(r'^$', ContestView.as_view(), name='index'),
        url(r'^details/(?P<id>\d+)$', ContestDetailsView.as_view(), name='details'),
        url(r'^(?P<contest_id>\d+)/(?P<problem_id>[A-Z])/$', ContestProblemView.as_view(), name='problem'),
        url(r'^report_status/$', report_task_status, name='report-status')
    ]
    return urlpatterns, 'onlineJudge', 'contest'
