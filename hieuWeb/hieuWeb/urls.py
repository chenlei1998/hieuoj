"""hieuWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from onlineJudge.views import home, contest, homework, widget, user, errors, problem, ranklist, status

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]

urlpatterns += [
    url(r'^$', home.HomeView.as_view(), name='home'),
    url(r'^homework/$', homework.HomeWorkView.as_view(), name='homework'),
    url(r'^problem/(?P<id>\d+)/$', problem.ProblemView.as_view(), name='problem'),
    url(r'^problem/report_status/$', problem.report_task_status, name='report-status'),
    url(r'^status/$', status.StatusView.as_view(), name='status'),
]

urlpatterns += [
    url(r'^widget/my_contest/', widget.MyContest.as_view()),
    url(r'^widget/system_info/', widget.SystemInfo.as_view()),
    url(r'^widget/my_submit/', widget.MySubmit.as_view()),
]

urlpatterns += [
    url(r'^user/', user.get_urls()),
    url(r'^error/', errors.get_urls()),
    url(r'^contest/', contest.get_urls()),
    url(r'^ranklist/', ranklist.get_urls())
]
