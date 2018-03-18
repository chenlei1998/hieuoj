# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelMultipleChoiceField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from django.db.models.query import QuerySet

from onlineJudge.models import *

from ckeditor.widgets import CKEditorWidget

admin.AdminSite.site_header = u'HIEUOJ|后台'


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    max_num = 1


class StudentProfileAdmin(admin.ModelAdmin):
    inlines = [StudentProfileInline]


class ProblemModelForm(forms.ModelForm):
    input = forms.CharField(strip=False, widget=forms.Textarea, label=u'输入')
    sample_input = forms.CharField(strip=False, widget=forms.Textarea, label=u'样例输入')
    output = forms.CharField(strip=False, widget=forms.Textarea, label=u'输出')
    sample_output = forms.CharField(strip=False, widget=forms.Textarea, label=u'样例输出')

    class Meta:
        exclude = []
        widgets = {
            'description': CKEditorWidget,
            'input_description': CKEditorWidget,
            'output_description': CKEditorWidget,
        }
        model = Problem


class ProblemModelAdmin(admin.ModelAdmin):
    form = ProblemModelForm
    search_fields = ['title']
    list_display = ['title', 'time_limit', 'memory_limit']


class CategoryModelAdmin(admin.ModelAdmin):
    filter_horizontal = ['problems']


class ContestModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContestModelForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance') is None:
            self.fields['problems'].queryset = self.fields['problems'].queryset.exclude(id__in=Contest.problems.through.objects.values('problem_id'))
        else:
            self.fields['problems'].queryset = self.fields['problems'].queryset.exclude(id__in=Contest.problems.through.objects.exclude(contest_id=self.instance.id).values('problem_id'))

    class Meta:
        exclude = []
        model = Contest
        widgets = {
            'problems': FilteredSelectMultiple(u'题目', False)
        }

    def clean(self):
        data = super(ContestModelForm, self).clean()
        if self.is_valid():
            # for problem in data['problems']:
            #     for obj in Contest.problems.through.objects.filter(problem=problem):
            #         if obj.contest.status() == 'running':
            #             self.add_error('problems', u'所选择的题目 "%s", 已经被正在进行的比赛 "%s"选中' % (problem.title, obj.contest.title))
            if data['end_date'] <= data['start_date']:
                self.add_error('end_date', u'结束时间必须大于开始时间')
        return data


class ContestModelAdmin(admin.ModelAdmin):
    form = ContestModelForm
    list_display = ['title', 'start_date', 'end_date']
    #filter_horizontal = ['problems']


class GlobalMsgModelAdmin(admin.ModelAdmin):
    list_display = ['msg', 'pub_date']

admin.site.unregister(User)
admin.site.register(User, StudentProfileAdmin)
admin.site.register(Problem, ProblemModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Contest, ContestModelAdmin)
admin.site.register(GlobalMsg, GlobalMsgModelAdmin)
