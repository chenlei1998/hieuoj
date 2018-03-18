# -*- coding: utf-8 -*-
from django.urls import reverse

from onlineJudge.forms import *
from onlineJudge.models import *


def global_context(request):
    if request.user.is_authenticated:
        submit_list = ProblemJudgeTask.objects.filter(user=request.user).order_by('-pub_date')[:5]
    else:
        submit_list = None
    context = {
        'user_count': StudentProfile.objects.count(),
        'problem_count': Problem.objects.count(),
        'submit_count': ProblemJudgeTask.objects.count(),
        'pending_count': ProblemJudgeTask.objects.filter(status='PENDING').count(),
        'my_submit_list': submit_list,
        'home_url': reverse('home'),
        'contest_url': reverse('contest:index'),
        'homework_url': reverse('homework'),
        'status_url': reverse('status'),
        'ranklist_url': reverse('ranklist:index'),
        'register_form': UserRegisterForm(auto_id=False),
        'login_form': UserLoginForm(auto_id=False),
        'solution_form': SolutionForm(auto_id=False),
        'global_msg': GlobalMsg.objects.all().order_by('-pub_date')
    }

    return context
