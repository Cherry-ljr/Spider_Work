from django.shortcuts import render

from django.shortcuts import render,render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import auth
from django.template import RequestContext
import time

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from UserProfile.models import User
# 第四个是auth中用户权限有关的类。auth可以设置每个用户的权限。

from .forms import LoginForm,RegisterForm,ProfileForm
from .models import Shop
# Create your views here.

# -*- coding: utf-8 -*-


def index(request):
    return render(request, 'index.html', {'username':'lijiarui'})

def DataAnalysis(request):
    return render(request, 'ljr.html')

def PageShow(request):
    pagedata = Shop.objects.all()
    return render(request, 'PageShow.html',{'pagedata':pagedata})

def userinfo_view(req):
    uname = req.session['user_name']
    userinfo = User.objects.filter(username = uname)
    
    if req.method == 'POST':
        uf = ProfileForm(req.POST)
        if uf.is_valid():
            
            #获得表单数据
            school = uf.cleaned_data['school']
            major = uf.cleaned_data['major']
            myClass = uf.cleaned_data['myClass']
            stuId = uf.cleaned_data['stuId']
            synopsis = uf.cleaned_data['synopsis']
            email = uf.cleaned_data['email']
            tel = uf.cleaned_data['tel']
            
            #添加到数据库（还可以加一些字段的处理）
            user = User.objects.get(username = uname)
            user.school = school
            user.major = major
            user.myClass = myClass
            user.stuId = stuId
            user.synopsis = synopsis
            user.email = email
            user.tel = tel
            user.save()
            
            #uf.save()
            #重定向到首页
            return HttpResponseRedirect('/index/')
        else :
            message = '用户信息修改有误！'
            return render(req, 'userinfo.html', locals())
    
    return render(req, 'userinfo.html', {'userinfo':userinfo});

#注册
def register_view(req):
    if req.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return HttpResponseRedirect("/index/")
    if req.method == 'POST':
        uf = RegisterForm(req.POST, req.FILES)
        if uf.is_valid():
            #获得表单数据
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #gender = uf.cleaned_data['gender']
            school = uf.cleaned_data['school']
            major = uf.cleaned_data['major']
            myClass = uf.cleaned_data['myClass']
            stuId = uf.cleaned_data['stuId']
            #headImage = uf.cleaned_data['headImage']
            headImage = req.FILES.get('headImage')

            with open(headImage.name,'wb') as f:
                for line in headImage:
                    f.write(line)

            synopsis = uf.cleaned_data['synopsis']
            email = uf.cleaned_data['email']
            tel = uf.cleaned_data['tel']

            # 判断用户是否存在
            user = auth.authenticate(username = username,password = password)
            if user:
                message = '用户名已存在！'
                return render(req, 'register.html', locals())


            #添加到数据库（还可以加一些字段的处理）
            user = User.objects.create_user(username = username,password = password)
            #user.gender = gender
            user.school = school
            user.major = major
            user.myClass = myClass
            user.stuId = stuId
            user.headImage = headImage
            user.synopsis = synopsis
            user.email = email
            user.tel = tel
            user.save()

            #添加到session
            req.session['is_login'] = True 
            req.session['user_id'] = user.id
            req.session['user_name'] = username
            #调用auth登录
            auth.login(req, user)
            #重定向到首页
            return HttpResponseRedirect('/index/')
        else:
            message = '用户名已存在！'
            return render(req, 'register.html', locals())
    else:
        uf = RegisterForm(req.POST)
    #将req 、页面 、以及context{}（要传入html文件中的内容包含在字典里）返回
    return  render(req,'register.html',locals())

#登陆
def login_view(req):
    if req.session.get('is_login', None):
        return HttpResponseRedirect('/index/')
    if req.method == 'POST':
        uf = LoginForm(req.POST)
        if uf.is_valid(): #确保用户名和密码都不为空
            #获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #获取的表单数据与数据库进行比较
            user = authenticate(username = username,password = password)
            if user:
                #比较成功，跳转index
                auth.login(req,user)
                req.session['is_login'] = True
                req.session['user_id'] = user.id
                req.session['user_name'] = username
                return  render(req, 'index.html')
            else:
                #比较失败，还在login
                message = "username or password wrong!"
                return render(req, 'login.html', locals())
        else :
            message = '所有字段都必须填写！'
            return render(req, 'login.html', locals())
    else:
        uf = LoginForm(req.POST)
    return render(req, 'login.html', locals())

#登出
def logout_view(req):
    if not req.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return HttpResponseRedirect("/index/")
    auth.logout(req)
    req.session.flush()
    # 或者使用下面的方法
    # del req.session['is_login']
    # del req.session['user_id']
    # del req.session['user_name']
    return HttpResponseRedirect("/index/")



