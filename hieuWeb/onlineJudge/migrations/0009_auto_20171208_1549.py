# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlineJudge', '0008_remove_studentprofile_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='_class',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u73ed\u7ea7'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='department',
            field=models.CharField(default='', max_length=255, verbose_name='\u5b66\u9662'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='major',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u4e13\u4e1a'),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='identity',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u8eab\u4efd\u8bc1\u53f7\u7801'),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='sex',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u6027\u522b'),
        ),
    ]