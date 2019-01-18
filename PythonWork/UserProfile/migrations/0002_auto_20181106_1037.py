# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-06 02:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='authority',
            field=models.CharField(blank=True, choices=[('SM', '超级管理员'), ('MG', '管理员'), ('US', '用户')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', '男'), ('W', ' 女')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='tel',
            field=models.CharField(blank=True, max_length=11),
        ),
    ]