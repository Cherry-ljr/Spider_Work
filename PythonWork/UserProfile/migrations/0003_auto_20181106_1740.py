# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-06 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0002_auto_20181106_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='authority',
            field=models.CharField(blank=True, choices=[('超级管理员', '超级管理员'), ('管理员', '管理员'), ('用户', '用户')], max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('男', '男'), ('女', ' 女')], max_length=2, null=True),
        ),
    ]
