# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from uuid import uuid1


class Department(models.Model):
    name = models.CharField(unique=True, max_length=255, verbose_name=u'学院')
    major = models.CharField(max_length=255, verbose_name=u'专业')
    _class = models.CharField(max_length=255, verbose_name=u'班级')

    def __unicode__(self):
        return "|".join([self.name, self.major, self._class])


class StudentProfile(models.Model):
    sno = models.CharField(unique=True, max_length=255, verbose_name=u"学号", db_index=True)
    name = models.CharField(max_length=255, verbose_name=u'姓名', db_index=True)
    department = models.CharField(max_length=255, verbose_name=u'学院', db_index=True)
    major = models.CharField(max_length=255, verbose_name=u'专业', blank=True, db_index=True)
    _class = models.CharField(max_length=255, verbose_name=u'班级', blank=True, db_index=True)
    sex = models.CharField(max_length=255, verbose_name=u'性别', blank=True)
    identity = models.CharField(max_length=255, verbose_name=u'身份证号码', blank=True)
    user = models.OneToOneField(User)

    class Meta:
        verbose_name = u'学生信息'
        verbose_name_plural = u'学生信息'


class GlobalMsg(models.Model):
    msg = models.TextField(verbose_name=u'消息')
    pub_date = models.DateTimeField(auto_now=True, verbose_name=u'发布时间')

    class Meta:
        verbose_name_plural = verbose_name = u'消息推送'

    def __unicode__(self):
        return self.msg


class Problem(models.Model):
    title = models.CharField(max_length=255, verbose_name=u'标题')
    description = models.TextField(verbose_name=u'问题描述')
    input_description = models.TextField(verbose_name=u'输入描述')
    output_description = models.TextField(verbose_name=u'输出描述')
    sample_input = models.TextField(verbose_name=u'样例输入')
    sample_output = models.TextField(verbose_name=u'样例输出')
    hint = models.TextField(verbose_name=u'提示', blank=True)
    input = models.TextField(verbose_name=u'问题输入')
    output = models.TextField(verbose_name=u'问题输出')
    time_limit = models.IntegerField(verbose_name=u'时间限制', help_text='MS')
    memory_limit = models.IntegerField(verbose_name=u'内存限制', help_text='MB')

    def __unicode__(self):
        return "{}-{}".format(self.id, self.title)

    class Meta:
        verbose_name_plural = verbose_name = u'题目'


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name=u'标题')
    problems = models.ManyToManyField(Problem, verbose_name=u'题目')

    class Meta:
        verbose_name_plural = verbose_name = u'题目分类'

    def __unicode__(self):
        return self.title


class Contest(models.Model):
    title = models.CharField(max_length=255, verbose_name=u'标题')
    start_date = models.DateTimeField(verbose_name=u'开始时间')
    end_date = models.DateTimeField(verbose_name=u'结束时间')
    problems = models.ManyToManyField(Problem, verbose_name=u'题目')

    def status(self):
        from django.utils import timezone
        if (timezone.now() > self.start_date) and (timezone.now() < self.end_date):
            return 'running'
        elif timezone.now() < self.start_date:
            return 'pending'
        elif timezone.now() > self.end_date:
            return 'finish'

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = verbose_name = u'赛事'


class AbstractJudgeTask(models.Model):
    """任务队列.
    """
    user = models.ForeignKey(User, verbose_name=u'提交用户')
    problem = models.ForeignKey(Problem, verbose_name=u'题目')
    task_id = models.UUIDField(verbose_name=u'任务ID', default=uuid1, unique=True)
    status = models.CharField(max_length=255, verbose_name=u'任务状态')
    lang = models.CharField(max_length=255, verbose_name=u'语言')
    code = models.TextField(verbose_name=u'代码')
    used_time = models.IntegerField(verbose_name=u'运行时间', default=0)
    used_memory = models.IntegerField(verbose_name=u'使用内存', default=0)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=u'提交时间')

    class Meta:
        abstract = True


class ProblemJudgeTask(AbstractJudgeTask):
    def __unicode__(self):
        return '|'.join([self.problem.title, self.user.username, self.status])


class ContestJudgeTask(AbstractJudgeTask):
    contest = models.ForeignKey(Contest, verbose_name=u'赛事')

    def __unicode__(self):
        return '|'.join([self.problem.title, self.user.username, self.contest.title, self.status])


class UserRankList(models.Model):
    user = models.ForeignKey(User)
    total_submit = models.IntegerField(default=0)
    ac_submit = models.IntegerField(default=0)
    solved_count = models.IntegerField(default=0, db_index=True)
