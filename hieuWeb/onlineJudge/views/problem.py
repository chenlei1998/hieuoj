# -*- coding: utf-8 -*-
from django.views import View
from django.db.models import Count, F
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse

from onlineJudge.models import Problem, Contest, Category, ProblemJudgeTask, UserRankList
from onlineJudge.forms import SolutionForm
from onlineJudge.utils import submit_task


class ProblemView(View):
    def get_contest_by_problem(self, problem):
        return Contest.problems.through.objects.filter(problem_id=problem.id).first()

    def get(self, request, id):
        try:
            problem = Problem.objects.get(id=id)
            contest = self.get_contest_by_problem(problem)

            # 题目处于私有状态
            if Category.problems.through.objects.filter(problem_id=problem.id).count() == 0:
                if (contest is not None) or (contest.status() == 'pending'):
                    return redirect('error:404')

            context = {
                'problem':
                    problem,
            }
            return render(request, 'problem.html', context)
        except Problem.DoesNotExist:
            return redirect('error:404')

    def post(self, request, id):
        try:
            problem = Problem.objects.get(id=id)
            solution_form = SolutionForm(request.POST)
            if request.user.is_authenticated() is False:
                data = {'status': 'unlogin'}
            elif solution_form.is_valid():
                data = {"status": "success"}
                task = ProblemJudgeTask(problem=problem,
                                        user=request.user,
                                        lang=solution_form.cleaned_data['lang'],
                                        code=solution_form.cleaned_data['code'],
                                        status=u'PENDING')
                task.save()
                submit_task(task.task_id, task.lang, task.code, problem.input, problem.output,
                            problem.memory_limit, problem.time_limit, reverse('report-status'))
            else:
                data = {'status': 'error', 'errors': dict([(k, v[0]) for k, v in solution_form.errors.items()])}
            return JsonResponse(data)
        except Problem.DoesNotExist:
            return redirect('error:404')


def report_task_status(request):
    task_id = request.GET.get('task_id')
    used_time = request.GET.get('used_time') or 0
    used_memory = request.GET.get('used_memory') or 0
    status = request.GET.get('status')
    try:
        task = ProblemJudgeTask.objects.get(task_id=task_id)
        task.status = status
        task.used_time = float(used_time)
        task.used_memory = float(used_memory)
        if status != 'RUNNING':
            rank, created = UserRankList.objects.get_or_create(user=task.user, defaults={'user': task.user})
            update = {
                'total_submit':
                    F('total_submit') + 1
            }
            if status == 'ACCEPTED':
                update['ac_submit'] = F('ac_submit') + 1
                if ProblemJudgeTask.objects.filter(problem_id=task.problem_id, user_id=task.user_id, status='ACCEPTED').exists() is False:
                    update['solved_count'] = F('solved_count') + 1
            UserRankList.objects.filter(user=task.user).update(**update)
        task.save()
        return JsonResponse({'status': 'success'})
    except ProblemJudgeTask.DoesNotExist:
        return redirect('error:404')
