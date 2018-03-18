# -*- coding: utf-8 -*-
import logging
import re
from random import choice

import requests
from captcha.image import ImageCaptcha
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.db import transaction
from onlineJudge.forms import *
from onlineJudge.models import StudentProfile, ProblemJudgeTask

logger = logging.getLogger(__name__)


class LoginCaptcha(View):
    """用户登录验证码.
    """
    image = ImageCaptcha(240, 50, font_sizes=[50, 40, 50])

    def get(self, request):
        str = "".join([choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in xrange(5)])
        request.session['captcha'] = str.lower()
        return HttpResponse(self.image.generate(str).read(), content_type="image/png")


class RegisterCaptcha(View):
    """用户注册验证码.
    """

    def get(self, request):
        with requests.Session() as s:
            r = s.get('http://222.247.62.198/jiaowu/other/CheckCode.aspx?datetime=az')
            request.session['jw_cookie'] = r.cookies.get_dict()
            return HttpResponse(r.content, content_type='image/jpeg')


class RegisterView(View):
    """用户注册.
    """

    def _valid_form(self, request, form):
        with requests.session() as s:
            if form.is_valid():
                if len(User.objects.filter(username=form.data['account'])):
                    form.add_error('account', u'这个账户已经被使用了')
                if 'jw_cookie' not in request.session:
                    form.add_error('captcha', u'验证码过期')
            if form.is_valid():
                cookies = request.session['jw_cookie']
                url = 'http://222.247.62.198/jiaowu/Login.aspx'
                r = s.get(url, cookies=cookies)
                data = {
                    '__VIEWSTATE': self._get_input_value(r.content, '__VIEWSTATE'),
                    '__EVENTVALIDATION': self._get_input_value(r.content, '__EVENTVALIDATION'),
                    '__VIEWSTATEGENERATOR': self._get_input_value(r.content, '__VIEWSTATEGENERATOR'),
                    'Account': form.data['account'],
                    'PWD': form.data['password'],
                    'CheckCode': form.data['captcha'],
                    'cmdok': ''
                }
                r = s.post(url, data, cookies=cookies)
                print len(r.history)
                if u"验证码不正确" in r.text:
                    form.add_error('captcha', u'验证码错误')
                elif len(r.history) and '.ASPXAUTH' in r.history[0].cookies:
                    url = 'http://222.247.62.198/jiaowu/JWXS/xsMenu.aspx'
                    r = s.get(url, cookies=cookies, allow_redirects=False)
                    usermain = re.findall(r'usermain=([a-zA-Z0-9]+)', r.content)[0]
                    url = 'http://222.247.62.198/jiaowu/JWXS/xskp/jwxs_xskp_like.aspx?usermain=' + usermain
                    r = s.get(url, cookies=cookies, allow_redirects=False)

                    fetch_info = lambda id: re.findall(r'<span id="' + id + '">(.*?)</span>', r.text)[0]

                    info = {
                        'department': fetch_info('lbxsh').strip(),
                        'major': fetch_info('lbzyh').strip(),
                        'class': fetch_info('lbbh').strip(),
                        'sno': fetch_info('Lbxh').strip(),
                        'name': re.findall(r'name="tbxsxm" type="text" value="(.*?)" ', r.text)[0].strip(),
                        'sex': re.findall(r'<option selected="selected" value="\d+">(.*)</option>', r.text)[0].strip(),
                        'identity': re.findall(r'name="tbsfzh" type="text" value="(.*?)" ', r.text)[0].strip()
                    }
                    return form.is_valid(), info
                else:
                    form.add_error('account', u'账号或密码错误')
                    form.add_error('password', u'账号或密码错误')
            return form.is_valid(), None

    def _get_input_value(self, html_str, id):
        result = re.findall(r'id="' + id + '" value="(.*)"', html_str)
        return result[0] if len(result) == 1 else ''

    def post(self, request):
        register_form = UserRegisterForm(request.POST)
        ret, info = self._valid_form(request, register_form)
        if ret:
            with transaction.atomic():
                user = User()
                user.username = info['sno']
                user.set_password(info['identity'][-6:])
                user.save()
                profile = StudentProfile()
                profile.name = info['name']
                profile.sex = info['sex']
                profile.identity = info['identity']
                profile.sno = info['sno']
                profile.user = user
                profile.department = info['department']
                profile.major = info['major']
                profile._class = info['class']
                profile.save()
            login(request, user)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "error", "errors": dict([(k, v[0]) for k, v in register_form.errors.items()])})


class LoginView(View):
    """用户登录.
    """

    def _valid_form(self, request, form):
        if form.is_valid():
            if 'captcha' not in request.session:
                form.add_error('captcha', u'验证码过期')
            elif form.data['captcha'] != request.session['captcha'].lower():
                del request.session['captcha']
                form.add_error('captcha', u'验证码错误')
        if form.is_valid():
            user = authenticate(username=form.data['account'], password=form.data['password'])
            if user is None:
                form.add_error('account', u'账号或密码错误')
                form.add_error('password', u'账号或密码错误')
            elif user.is_active is False:
                form.add_error('account', u'账号被停用')
            else:
                login(request, user)
        return form.is_valid()

    def post(self, request):
        login_form = UserLoginForm(request.POST)
        if self._valid_form(request, login_form):
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "error", "errors": dict([(k, v[0]) for k, v in login_form.errors.items()])})


class LogoutView(View):
    """注销登录.
    """

    def get(self, request):
        logout(request)
        if request.META.get('HTTP_REFERER') is not None:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return redirect('home')


class ChangePasswordView(TemplateView):
    """修改密码.
    """
    template_name = 'change_password.html'

    def post(self, request):
        form = ChangePasswordForm(request, request.POST)
        context = self.get_context_data()
        if form.is_valid():
            if request.user.is_authenticated():
                print form.cleaned_data
                request.user.set_password(form.cleaned_data['new_password'])
                request.user.save()
            context['success'] = True
        else:
            context['form'] = form
            context['success'] = False
        return self.render_to_response(context)


class ResetPasswordView(TemplateView):
    """重置密码.
    """
    template_name = 'reset_password.html'

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        context = self.get_context_data()

        if form.is_valid():
            profile = StudentProfile.objects.get(user__username=form.cleaned_data['username'])
            profile.user.set_password(profile.identity[-6:])
            profile.user.save()
            context['success'] = True
        else:
            print form.errors
            context['form'] = form
            context['success'] = False

        return self.render_to_response(context)

class ChangYanUserInfo(View):
    def get(self, request):
        import json
        data = {
            'is_login': 0
        }
        if request.user.is_authenticated():
            data = {
                'is_login': 1,
                'user': {
                    'user_id': request.user.id,
                    'nickname': request.user.username,
                    'sign': '',
                }
            }
        ret = [request.GET['callback'], '(', json.dumps(data), ')']
        return HttpResponse(''.join(ret))


class ChangYanLogout(View):
    def get(self, request):
        import json
        data = {
            'code': 1,
            'reload_page': 0
        }
        if request.user.is_authenticated():
            data['reload_page'] = 1
            logout(request)
        ret = [request.GET['callback'], '(', json.dumps(data), ')']
        return HttpResponse(''.join(ret))


class ACRatio(View):
    def get(self, request):
        import json
        from itertools import groupby
        from datetime import timedelta, datetime
        from collections import Counter
        from math import ceil
        entity_sets = ProblemJudgeTask.objects.filter(pub_date__range=((datetime.utcnow() - timedelta(days=30)), datetime.utcnow())).order_by('pub_date')
        status_list = []
        for date, group in groupby(entity_sets, key=lambda entity: entity.pub_date.date()):
            counter = Counter([entity.status for entity in group])
            ac_count = counter['ACCEPTED'] * 1.0
            other_count = sum(counter.values())
            status_list.append((str(date), (ac_count / other_count) * 100))
        return HttpResponse(json.dumps(status_list))

        
def get_urls():
    from django.conf.urls import url
    urlpatterns = [
        url(r'^register/captcha/$', RegisterCaptcha.as_view(), name='register-captcha'),
        url(r'^register/$', RegisterView.as_view(), name='register'),
        url(r'^login/captcha/$', LoginCaptcha.as_view(), name='login-captcha'),
        url(r'^password/change/$', ChangePasswordView.as_view(), name='change-password'),
        url(r'^password/reset/$', ResetPasswordView.as_view(), name='reset-password'),
        url(r'^login/$', LoginView.as_view(), name='login'),
        url(r'^logout/$', LogoutView.as_view(), name='logout'),
        url(r'^changyan/info/$', ChangYanUserInfo.as_view(), name='cy-userinfo'),
        url(r'^changyan/logout', ChangYanLogout.as_view(), name='cy-logout'),
        url(r'^acratio/', ACRatio.as_view(), name='acratio'),
    ]
    return urlpatterns, 'onlineJudge', 'user'