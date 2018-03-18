# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

from django.utils.translation import ungettext_lazy
from onlineJudge.models import StudentProfile

class UserRegisterForm(forms.Form):
    """用户注册表单.
    """
    account = forms.CharField(max_length=16,
                              widget=forms.TextInput(attrs={'placeholder': u'登录教务网时使用的账号', 'class': 'form-control'}),
                              error_messages={"required": u"请填入登录教务网时使用的账号"})

    password = forms.CharField(max_length=16,
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': u'登录教务网时使用的密码', 'class': 'form-control'}),
                               error_messages={'required': u'请填入登录教务网时使用的密码'})

    captcha = forms.CharField(max_length=4, min_length=4,
                              widget=forms.TextInput(attrs={'placeholder': u'请输入下方验证码', 'class': 'form-control'}),
                              error_messages={'required': u'请填入验证码'})


class UserLoginForm(forms.Form):
    """用户登录表单.
    """

    account = forms.CharField(max_length=16, min_length=4,
                              widget=forms.TextInput(attrs={'placeholder': u'你的学号', 'class': 'form-control'}),
                              error_messages={"required": u"请填入账号", 'min_length': u'账号长度最少为%(limit_value)d位', 'max_length': u'账号长度最多为%(limit_value)d位'})

    password = forms.CharField(max_length=16, min_length=6,
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': u'默认密码为身份证后六位', 'class': 'form-control'}),
                               error_messages={'required': u'请填入密码', 'min_length': u'密码长度最少为%(limit_value)d位', 'max_length': u'密码长度最多为%(limit_value)d位'})

    captcha = forms.CharField(max_length=5, min_length=5,
                              widget=forms.TextInput(attrs={'placeholder': u'请输入下方验证码', 'class': 'form-control'}),
                              error_messages={'required': u'请填入验证码', 'min_length': u'验证码长度为%(limit_value)d位', 'max_length': u'验证码长度为%(limit_value)d位'})

    remember_status = forms.BooleanField(widget=forms.CheckboxInput(), required=False)


class SolutionForm(forms.Form):
    """用户提交解答表单.
    """
    lang_choices = (
        ('', u'请选择语言'),
        ('GCC', 'GCC'),
        ('G++', 'G++'),
        ('JAVA', 'JAVA'),
        ('C#', 'C#'),
    )
    lang = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=lang_choices))
    code = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': u'请填入你的解答'}))

    def clean(self):
        data = super(SolutionForm, self).clean()
        if data['lang'] not in dict(self.lang_choices):
            self.add_error('lang', u'不支持所选择的语言')
        return data


class ChangePasswordForm(forms.Form):
    """更改密码表单
    """

    old_password = forms.CharField(max_length=16, min_length=6)
    new_password = forms.CharField(max_length=16, min_length=6)

    def __init__(self, request, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        old_password = self.cleaned_data.get('old_password')
        if self.is_valid() and self.request.user.check_password(old_password) is False:
            self.add_error('old_password', u'原始密码错误')
        return self.cleaned_data


class ResetPasswordForm(forms.Form):
    """重置密码表单.
    """
    real_name = forms.CharField(max_length=8, min_length=1)
    username = forms.CharField(max_length=16, min_length=4)
    identity = forms.CharField(max_length=18, min_length=18)

    def clean(self):
        username = self.cleaned_data.get('username')
        real_name = self.cleaned_data.get('real_name')
        identity = self.cleaned_data.get('identity')
        if self.is_valid():
            if StudentProfile.objects.filter(user__username=username).exists():
                user = StudentProfile.objects.get(user__username=username).user
                if user.studentprofile.name != real_name:
                    self.add_error('real_name', u'真实姓名核对失败, 请检查')
                if user.studentprofile.identity != identity:
                    self.add_error('identity', u'身份证号码核对失败, 请检查')
            else:
                self.add_error('username', u'用户名不存在')
        return self.cleaned_data



