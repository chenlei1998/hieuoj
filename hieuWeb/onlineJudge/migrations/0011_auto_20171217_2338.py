# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-17 15:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onlineJudge', '0010_auto_20171208_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homework',
            name='problems',
        ),
        migrations.RemoveField(
            model_name='homework',
            name='receiver',
        ),
        migrations.DeleteModel(
            name='Homework',
        ),
    ]