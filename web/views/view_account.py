#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 17:23


from django.shortcuts import render, redirect, HttpResponse
from rbac.service.init_permission import init_permission
from rbac import models as rbac_models
from web import models as web_models
from web.forms import form_account
from django.contrib import auth
import datetime


def login(request):
    if request.method == 'GET':
        loginForm = form_account.LoginForm()
        return render(request, 'login_pro.html', {'loginForm': loginForm})

    else:
        loginForm = form_account.LoginForm(request.POST)

        if loginForm.is_valid():
            username = loginForm.cleaned_data['username']
            password = loginForm.cleaned_data['password']
            usertype = loginForm.cleaned_data['usertype']

            current_user = rbac_models.UserProfile.objects.filter(username=username).values('roles__usertype').first()

            if current_user == None:
                db_usertype = None
            else:
                db_usertype = current_user['roles__usertype']

            user = auth.authenticate(username=username, password=password)

            if str(usertype) != str(db_usertype) or user is None:
                return render(request, 'login_pro.html', {'loginForm': loginForm, 'msg': '用户名或密码或用户类型错误,请重新登陆！'})

            else:
                auth.login(request, user)  # session写操作
                init_permission(username,request)
                if usertype == '管理员':
                    return redirect('/admin_index/')
                elif usertype == '党员用户':
                    return redirect('/member_index/')
                elif usertype == '积极分子':
                    return redirect('/activist_index/')
        else:
            return render(request, 'login_pro.html', {'loginForm': loginForm})


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def set_password(request, old_password, new_password, repeat_password):
    """修改用户密码"""

    user = request.user

    if user.check_password(old_password):
        if new_password != repeat_password:
            status = 'repeat_error'

        else:
            user.set_password(new_password)
            user.save()
            status = 'ok'
        return status

    else:
        return 'password_error'


def test(request):

    # user = models.UserProfile.objects.create_user(username='root', password='123456', usertype=1, email='123@qq.com')

    # rbac_models.Role.objects.create(usertype='1')
    # rbac_models.Role.objects.create(usertype='2')
    # rbac_models.Role.objects.create(usertype='3')

    role1 = rbac_models.Role.objects.filter(usertype='管理员').first()
    role2 = rbac_models.Role.objects.filter(usertype='党员用户').first()
    role3 = rbac_models.Role.objects.filter(usertype='积极分子').first()
    user = rbac_models.UserProfile.objects.create_superuser(username='admin', password='1234', roles_id=role1.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='tiger', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='lion', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='puma', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='bear', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='polar', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='wolf', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='snake', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='fox', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='dog', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='pig', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='rabbit', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='bee', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='bird', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='bull', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='cat', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='cow', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='cock', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='carp', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='duck', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='fish', password='1234', roles_id=role2.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='goat', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='horse', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='kitty', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='mouse', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='mare', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='panda', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='swan', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='sheep', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='vole', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='yak', password='1234', roles_id=role3.rid, email='123@qq.com')
    user = rbac_models.UserProfile.objects.create_user(username='zabra', password='1234', roles_id=role3.rid, email='123@qq.com')
    #

    # member = web_models.Member.objects.create()

    # user = rbac_models.UserProfile.objects.filter(username='admin').first()
    # admina = web_models.Admin.objects.create(admin_name='熊大' ,admin_gender='M',admin_phone=13422345636,usertype_id=user.uid)
    # admina = web_models.Admin.objects.filter(admin_id=1).update(usertype_id=user.uid)

    return HttpResponse('ok')
    # if request.method == 'GET':
    #     loginForm = form_account.LoginForm()
    #     return render(request, 'login_pro.html', {'loginForm': loginForm})


def add_member(request):
    """增加党员用户测试数据"""

    # user = rbac_models.UserProfile.objects.filter(username='tiger').first()
    # member = web_models.Member.objects.create_user(member_name='李毅', member_gender='男', member_phone='', email='123@qq.com')

    # role1 = rbac_models.Role.objects.filter(usertype='党员用户').first()
    # user = rbac_models.UserProfile.objects.create_user(username='pick', password='1234', roles_id=role1.rid, email='123@qq.com')
    # user = rbac_models.UserProfile.objects.create_user(username='luffy', password='1234', roles_id=role1.rid, email='123@qq.com')
    # user = rbac_models.UserProfile.objects.create_user(username='boom', password='1234', roles_id=role1.rid, email='123@qq.com')

    today = datetime.date.today()
    data = web_models.Member.objects.filter(member_id=23).first()

    dd = (today - data.regular_date).days

    return HttpResponse('ok')


