from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser


class Shop(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    deal = models.CharField(max_length=200)
    shop = models.CharField(max_length=200)



class User(AbstractUser):
    GENDER_CHOICE = (('男', '男'), ('女', '女'))
    USER_AUTHORITY_CHOSE = (('超级管理员', '超级管理员'), ('管理员', '管理员'), ('用户', '用户'))
    
    nickname = models.CharField(max_length=50, blank=True)
    #gender = models.CharField(max_length=4, choices=GENDER_CHOICE, null=True, blank=True)                # 性别
    school = models.CharField(max_length=30, null=True, blank=True)                                      # 学校
    major = models.CharField(max_length=10, null=True, blank=True)                                       # 专业
    myClass = models.CharField(max_length=15, null=True, blank=True)                                     # 班级
    stuId = models.CharField(max_length=20, null=True, blank=True)                                       # 学号
    headImage = models.ImageField(upload_to='headImage', null=True, blank=True)                          # 头像
    synopsis = models.TextField(null=True, blank=True)                                                   # 简介
    tel = models.CharField(max_length=11, blank=True)                                                   # 手机号（不可为空）
    authority = models.CharField(max_length=5, choices=USER_AUTHORITY_CHOSE, null=True, blank=True)      # 用户权限


    class Meta(AbstractUser.Meta):
        pass
