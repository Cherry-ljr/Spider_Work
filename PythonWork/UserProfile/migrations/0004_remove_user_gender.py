# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-06 16:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0003_auto_20181106_1740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
    ]
