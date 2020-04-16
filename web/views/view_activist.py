#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 17:23

from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import authenticate, login, logout
from rbac import models as rbac_models
from web import models as web_models
from web.forms import form_activist
from web.forms import form_account
from web.views import view_account



def activist_index(request):
    username = request.user
    # 提取新用户识别字段
    is_new_user = rbac_models.UserProfile.objects.filter(username=username).values('is_newuser').first()
    flag = is_new_user['is_newuser']

    # 如果是新用户，则需要完善个人信息
    if flag:
        return render(request, 'activist_index.html', {'user': username, 'flag': True})
    else:
        admin_count = rbac_models.UserProfile.objects.filter(roles__usertype='管理员').all().count()
        formal_member_count = web_models.Member.objects.exclude(is_out_team='是').filter(member_status='正式党员').count()
        informal_member_count = web_models.Member.objects.exclude(is_out_team='是').filter(member_status='预备党员').count()
        activist_count = web_models.Activist.objects.all().count()

        party_info = web_models.PartyInfo.objects.filter(id=1).first()
        party_secretary = web_models.Member.objects.filter(member_duty='支部书记').first()
        party_organizer = web_models.Member.objects.filter(member_duty='组织委员').first()
        party_publicity = web_models.Member.objects.filter(member_duty='宣传委员').first()
        party_discipline = web_models.Member.objects.filter(member_duty='纪检委员').first()

        context = {
            'admin_count': admin_count,
            'formal_member_count': formal_member_count,
            'informal_member_count': informal_member_count,
            'activist_count': activist_count,
            'user': username,
            'party_info': party_info,
            'party_secretary': party_secretary,
            'party_organizer': party_organizer,
            'party_publicity': party_publicity,
            'party_discipline': party_discipline,
        }

        return render(request, 'activist_index.html', context)


def activist_profile(request):
    """个人信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Admin中的数据
    data_activist = web_models.Activist.objects.filter(user_account_id=data_profile['uid']).first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_activist.activist_name,
        'usertype': data_profile['roles__usertype'],
        'gender': data_activist.activist_gender,
        'email': data_profile['email'],
        'phone': data_activist.activist_phone,
        'apply_date': data_activist.apply_date,
        'voluntary_time': data_activist.voluntary_time,
    }

    return render(request, 'activist_profile.html', {'user': username, 'data_list': data_list})


def activist_addinfo(request):
    """"新用户完善信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'roles__usertype',
                                                                                    'is_newuser', 'activist__activist_name',
                                                                                    'activist__activist_gender').first()
    data_list = {
        'username': username,
        'usertype': data_profile['roles__usertype'],
        'activist_name': data_profile['activist__activist_name'],
        'activist_gender': data_profile['activist__activist_gender'],
    }

    # 如果不是新用户
    if not data_profile['is_newuser']:
        tag = True
        return render(request, 'activist_addinfo.html', {'user': username, 'tag': tag})

    if request.method == 'GET':

        addinfoForm = form_activist.InfoForm()

        return render(request, 'activist_addinfo.html',
                      {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})

    else:
        addinfoForm = form_activist.InfoForm(request.POST)

        if addinfoForm.is_valid():
            activist_email = addinfoForm.cleaned_data['activist_email']
            activist_phone = addinfoForm.cleaned_data['activist_phone']
            apply_date = addinfoForm.cleaned_data['apply_date']
            voluntary_time = addinfoForm.cleaned_data['voluntary_time']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=activist_email, is_newuser=0)
            # 更新Admin信息
            web_models.Activist.objects.filter(user_account__username=username).update(activist_phone=activist_phone,
                                                                                     apply_date=apply_date,
                                                                                     voluntary_time=voluntary_time)
            flag = True

            return render(request, 'activist_addinfo.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'addinfoForm': addinfoForm})

        else:
            return render(request, 'activist_addinfo.html',
                          {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})


def activist_profile_alter(request):
    """修改个人信息"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Activist中的数据
    data_activist = web_models.Activist.objects.filter(user_account_id=data_profile['uid']).first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_activist.activist_name,
        'usertype': data_profile['roles__usertype'],
        'gender': data_activist.activist_gender,
        'email': data_profile['email'],
        'phone': data_activist.activist_phone,
        'apply_date': data_activist.apply_date,
        'voluntary_time': data_activist.voluntary_time,
    }

    init_data = {
        'activist_name': data_activist.activist_name,
        'activist_gender': data_activist.activist_gender,
        'activist_email': data_profile['email'],
        'activist_phone': data_activist.activist_phone,
        'apply_date': data_activist.apply_date,
        'voluntary_time': data_activist.voluntary_time,
    }

    if request.method == 'GET':

        alterinfoForm = form_activist.EditInfoForm(initial=init_data)

        return render(request, 'activist_profile_alter.html',
                      {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})

    else:

        alterinfoForm = form_activist.EditInfoForm(request.POST)

        if alterinfoForm.is_valid():
            activist_name = alterinfoForm.cleaned_data['activist_name']
            activist_gender = alterinfoForm.cleaned_data['activist_gender']
            activist_email = alterinfoForm.cleaned_data['activist_email']
            activist_phone = alterinfoForm.cleaned_data['activist_phone']
            apply_date = alterinfoForm.cleaned_data['apply_date']
            voluntary_time = alterinfoForm.cleaned_data['voluntary_time']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=activist_email)
            # 更新Member信息
            web_models.Activist.objects.filter(user_account_id=data_profile['uid']).update(activist_name=activist_name,
                                                                                           activist_gender=activist_gender,
                                                                                           activist_phone=activist_phone,
                                                                                           apply_date=apply_date,
                                                                                         voluntary_time=voluntary_time)
            flag = True
            return render(request, 'activist_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'alterinfoForm': alterinfoForm})

        else:
            return render(request, 'activist_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})


def activist_pwd_alter(request):
    """修改用户密码"""

    username = request.user

    if request.method == 'GET':
        pwdForm = form_account.PwdForm()
        return render(request, 'activist_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})

    else:

        pwdForm = form_account.PwdForm(request.POST)
        if pwdForm.is_valid():
            old_password = pwdForm.cleaned_data['old_password']
            new_password = pwdForm.cleaned_data['new_password']
            repeat_password = pwdForm.cleaned_data['repeat_password']

            status = view_account.set_password(request, old_password, new_password, repeat_password)

            if status == 'password_error':
                return render(request, 'activist_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '原密码输入错误!'})

            elif status == 'repeat_error':
                return render(request, 'activist_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '两次新密码输入不一致!'})

            else:
                logout(request)
                return render(request, 'activist_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '修改成功，请重新登录!'})

        else:
            return render(request, 'activist_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})


def activist_my_meeting(request):
    """我的会议"""

    username = request.user

    name = web_models.Activist.objects.filter(user_account__username=username).values('activist_name').first()
    data_meeting = web_models.ActivistMeetingRecord.objects.all().order_by('date')

    data_list_attend = []
    for item in data_meeting:
        attendance = eval(item.attendance)
        if name['activist_name'] in attendance:
            data_list_attend.append(item)

    data_list_absent = []
    for item in data_meeting:
        attendance = eval(item.absence)
        if name['activist_name'] in attendance:
            data_list_absent.append(item)

    # 将人员名单转为list类型
    for row in data_list_attend:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    for row in data_list_absent:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    count = {
        'attend': len(data_list_attend),
        'absent': len(data_list_absent),
    }

    return render(request, 'activist_my_meeting.html',
                  {'count': count, 'data_list_attend': data_list_attend, 'data_list_absent': data_list_absent})


def activist_my_lecture(request):
    """我的党课"""

    username = request.user

    name = web_models.Activist.objects.filter(user_account__username=username).values('activist_name').first()
    data_meeting = web_models.ActivistLectureRecord.objects.all().order_by('date')

    data_list_attend = []
    for item in data_meeting:
        attendance = eval(item.attendance)
        if name['activist_name'] in attendance:
            data_list_attend.append(item)

    data_list_absent = []
    for item in data_meeting:
        attendance = eval(item.absence)
        if name['activist_name'] in attendance:
            data_list_absent.append(item)

    # 将人员名单转为list类型
    for row in data_list_attend:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    for row in data_list_absent:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    count = {
        'attend': len(data_list_attend),
        'absent': len(data_list_absent),
    }

    return render(request, 'activist_my_lecture.html',
                  {'count': count, 'data_list_attend': data_list_attend, 'data_list_absent': data_list_absent})






