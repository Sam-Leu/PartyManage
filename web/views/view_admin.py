#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 17:23

from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.db.models import Count
from rbac import models as rbac_models
from web import models as web_models
from web.forms import form_admin
from web.forms import form_account
from web.views import view_account
from web.pages import PageInfo

import time
import json
import datetime


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


@login_required
def admin_index(request):
    username = request.user
    # 提取新用户识别字段
    is_new_user = rbac_models.UserProfile.objects.filter(username=username).values('is_newuser').first()
    flag = is_new_user['is_newuser']

    # 一登录系统就把转正日期、入党日期、转入日期和转出日期设置为当天
    today = datetime.date.today()
    web_models.DateSet.objects.filter(id=1).update(regular_date_set=today, first_date_set=today, in_date_set=today,
                                                   out_date_set=today)

    # 如果是新用户，则需要完善个人信息
    if flag:
        return render(request, 'admin_index.html', {'user': username, 'flag': True})
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

        return render(request, 'admin_index.html', context)


@login_required
def admin_profile(request):
    """个人信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Admin中的数据
    data_admin = web_models.Admin.objects.filter(user_account_id=data_profile['uid']).values('admin_name',
                                                                                             'admin_gender',
                                                                                             'admin_phone').first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_admin['admin_name'],
        'usertype': data_profile['roles__usertype'],
        'gender': data_admin['admin_gender'],
        'email': data_profile['email'],
        'phone': data_admin['admin_phone'],
    }

    return render(request, 'admin_profile.html', {'user': username, 'data_list': data_list})


def admin_addinfo(request):
    """"新用户完善信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'roles__usertype',
                                                                                    'is_newuser').first()
    data_list = {
        'username': username,
        'usertype': data_profile['roles__usertype'],
    }

    # 如果不是新用户
    if not data_profile['is_newuser']:
        tag = True
        return render(request, 'admin_addinfo.html', {'user': username, 'tag': tag})

    if request.method == 'GET':

        addinfoForm = form_admin.InfoForm()

        return render(request, 'admin_addinfo.html',
                      {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})

    else:
        addinfoForm = form_admin.InfoForm(request.POST)

        if addinfoForm.is_valid():
            admin_name = addinfoForm.cleaned_data['admin_name']
            admin_gender = addinfoForm.cleaned_data['admin_gender']
            admin_email = addinfoForm.cleaned_data['admin_email']
            admin_phone = addinfoForm.cleaned_data['admin_phone']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=admin_email, is_newuser=0)
            account = rbac_models.UserProfile.objects.filter(username=username).first()
            # 更新Admin信息
            web_models.Admin.objects.filter(user_account__username=username).update(admin_name=admin_name,
                                                                                    admin_gender=admin_gender,
                                                                                    admin_phone=admin_phone)

            flag = True

            return render(request, 'admin_addinfo.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'addinfoForm': addinfoForm})

        else:
            return render(request, 'admin_addinfo.html',
                          {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})


def admin_profile_alter(request):
    """修改个人信息"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Admin中的数据
    data_admin = web_models.Admin.objects.filter(user_account_id=data_profile['uid']).values('admin_name',
                                                                                             'admin_gender',
                                                                                             'admin_phone').first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_admin['admin_name'],
        'usertype': data_profile['roles__usertype'],
        'gender': data_admin['admin_gender'],
        'email': data_profile['email'],
        'phone': data_admin['admin_phone'],
    }

    init_data = {
        'admin_name': data_admin['admin_name'],
        'admin_gender': data_admin['admin_gender'],
        'admin_email': data_profile['email'],
        'admin_phone': data_admin['admin_phone'],
    }

    if request.method == 'GET':

        alterinfoForm = form_admin.InfoForm(initial=init_data)

        return render(request, 'admin_profile_alter.html',
                      {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})

    else:

        alterinfoForm = form_admin.InfoForm(request.POST)

        if alterinfoForm.is_valid():
            admin_name = alterinfoForm.cleaned_data['admin_name']
            admin_gender = alterinfoForm.cleaned_data['admin_gender']
            admin_email = alterinfoForm.cleaned_data['admin_email']
            admin_phone = alterinfoForm.cleaned_data['admin_phone']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=admin_email)
            # 更新Admin信息
            web_models.Admin.objects.filter(user_account_id=data_profile['uid']).update(admin_name=admin_name,
                                                                                        admin_gender=admin_gender,
                                                                                        admin_phone=admin_phone)
            flag = True
            return render(request, 'admin_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'alterinfoForm': alterinfoForm})

        else:
            return render(request, 'admin_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})


@login_required
def admin_pwd_alter(request):
    """修改用户密码"""

    username = request.user

    if request.method == 'GET':
        pwdForm = form_account.PwdForm()
        return render(request, 'admin_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})

    else:

        pwdForm = form_account.PwdForm(request.POST)
        if pwdForm.is_valid():
            old_password = pwdForm.cleaned_data['old_password']
            new_password = pwdForm.cleaned_data['new_password']
            repeat_password = pwdForm.cleaned_data['repeat_password']

            status = view_account.set_password(request, old_password, new_password, repeat_password)

            if status == 'password_error':
                return render(request, 'admin_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '原密码输入错误!'})

            elif status == 'repeat_error':
                return render(request, 'admin_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '两次新密码输入不一致!'})

            else:
                logout(request)
                return render(request, 'admin_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '修改成功，请重新登录!'})

        else:
            return render(request, 'admin_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})


def admin_party_affairs(request):
    """党务管理页面"""

    return render(request, 'admin_party_affairs.html')


def admin_meeting_record(request):
    """会议记录页面"""

    username = request.user
    # 获取第几页
    current_page = request.GET.get('page')
    # 获取数据总条数
    all_count = web_models.MeetingRecord.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_meeting_record', 5)

    # 按照date排序读取数据
    data = web_models.MeetingRecord.objects.all().order_by('date')[page_info.start():page_info.end()]

    for row in data:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    return render(request, 'admin_meeting_record.html', {'user': username, 'data': data, 'page_info': page_info})


def get_all_member(request):
    """获取全部党员(不包括申请转出党员)信息"""

    time.sleep(0.5)

    temp_list = web_models.Member.objects.exclude(is_out_team='是').all()
    member_list = []
    for item in temp_list:
        member_list.append({'id': item.member_id, 'member_name': item.member_name})

    return HttpResponse(json.dumps(member_list))


def get_one_meeting(request):
    """获取一个会议信息"""

    time.sleep(0.5)

    uid = request.GET.get('id')
    data = web_models.MeetingRecord.objects.filter(id=uid).first()

    member = web_models.Member.objects.exclude(is_out_team='是').all()
    member_list = []
    for item in member:
        member_list.append(item.member_name)

    data_list = []
    data_list.append({
        'id': data.id,
        'date': data.date,
        'place': data.place,
        'title': data.title,
        'member': member_list,
        'attendance': eval(data.attendance),
        'absence': eval(data.absence),
    })

    # 删除member中存在的attendance
    for item in data_list[0]['attendance']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    # 删除member中存在的absence
    for item in data_list[0]['absence']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    return HttpResponse(json.dumps(data_list, cls=DateEncoder))


def set_meeting_record(request):
    """添加和修改会议信息"""

    ret = {'status': True, 'msg': None}

    nid = request.POST.get('id')
    date = request.POST.get('date')
    place = request.POST.get('place')
    flag = request.POST.get('flag')
    title = request.POST.get('title')
    attend_list = request.POST.getlist('attend_list')
    absent_list = request.POST.getlist('absent_list')

    if date == '' or title == '' or place == '' or attend_list == ['']:
        ret['status'] = False
        ret['msg'] = '输入信息有误，请重新输入！'
        return HttpResponse(json.dumps(ret))

    else:
        attend_num = len(attend_list)

        if absent_list == ['']:
            absent_num = 0
        else:
            absent_num = len(absent_list)

        # 添加会议
        if flag == 'add':
            web_models.MeetingRecord.objects.create(date=date, place=place, title=title, attend_num=attend_num,
                                                    absent_num=absent_num, attendance=attend_list,
                                                    absence=absent_list)
        # 修改会议
        else:
            web_models.MeetingRecord.objects.filter(id=nid).update(date=date, place=place, title=title,
                                                                   attend_num=attend_num,
                                                                   absent_num=absent_num, attendance=attend_list,
                                                                   absence=absent_list)

        return HttpResponse(json.dumps(ret))


def del_one_meeting(request):
    """删除一个会议"""

    time.sleep(2)

    nid = request.GET.get('nid')

    web_models.MeetingRecord.objects.filter(id=nid).delete()

    return redirect('/admin_meeting_record/')


def admin_lecture_record(request):
    """党课记录页面"""

    username = request.user
    # 获取第几页
    current_page = request.GET.get('page')
    # 获取数据总条数
    all_count = web_models.LectureRecord.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_lecture_record', 5)

    # 按照date排序读取数据
    data = web_models.LectureRecord.objects.all().order_by('date')[page_info.start():page_info.end()]

    for row in data:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    return render(request, 'admin_lecture_record.html', {'user': username, 'data': data, 'page_info': page_info})


def get_one_lecture(request):
    """获取一个党课信息"""

    time.sleep(0.5)

    uid = request.GET.get('id')
    data = web_models.LectureRecord.objects.filter(id=uid).first()

    member = web_models.Member.objects.exclude(is_out_team='是').all()
    member_list = []
    for item in member:
        member_list.append(item.member_name)

    data_list = []
    data_list.append({
        'id': data.id,
        'date': data.date,
        'place': data.place,
        'title': data.title,
        'member': member_list,
        'attendance': eval(data.attendance),
        'absence': eval(data.absence),
    })

    # 删除member中存在的attendance
    for item in data_list[0]['attendance']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    # 删除member中存在的absence
    for item in data_list[0]['absence']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    return HttpResponse(json.dumps(data_list, cls=DateEncoder))


def set_lecture_record(request):
    """添加和修改党课信息"""

    ret = {'status': True, 'msg': None}

    nid = request.POST.get('id')
    date = request.POST.get('date')
    place = request.POST.get('place')
    flag = request.POST.get('flag')
    title = request.POST.get('title')
    attend_list = request.POST.getlist('attend_list')
    absent_list = request.POST.getlist('absent_list')

    if date == '' or title == '' or place == '' or attend_list == ['']:
        ret['status'] = False
        ret['msg'] = '输入信息有误，请重新输入！'
        return HttpResponse(json.dumps(ret))

    else:
        attend_num = len(attend_list)

        if absent_list == ['']:
            absent_num = 0
        else:
            absent_num = len(absent_list)

        # 添加会议
        if flag == 'add':
            web_models.LectureRecord.objects.create(date=date, place=place, title=title, attend_num=attend_num,
                                                    absent_num=absent_num, attendance=attend_list,
                                                    absence=absent_list)
        # 修改会议
        else:
            web_models.LectureRecord.objects.filter(id=nid).update(date=date, place=place, title=title,
                                                                   attend_num=attend_num,
                                                                   absent_num=absent_num, attendance=attend_list,
                                                                   absence=absent_list)

        return HttpResponse(json.dumps(ret))


def del_one_lecture(request):
    """删除一个党课"""

    time.sleep(2)

    nid = request.GET.get('nid')

    web_models.LectureRecord.objects.filter(id=nid).delete()

    return redirect('/admin_lecture_record/')


def admin_reward_punish(request):
    """奖惩管理页面"""

    username = request.user
    current_page = request.GET.get('page')
    all_count = web_models.Member.objects.exclude(is_out_team='是').all().count()
    page_info = PageInfo(current_page, all_count, 7, '/admin_reward_punish', 5)
    user_list = web_models.Member.objects.exclude(is_out_team='是').all()[page_info.start():page_info.end()]

    info = web_models.RewardAndPunish.objects.filter(id='1').values('reward_1', 'reward_2', 'reward_3', 'punish_1',
                                                                    'punish_2', 'punish_3', ).first()

    init_data = {
        'reward_1': info['reward_1'],
        'reward_2': info['reward_2'],
        'reward_3': info['reward_3'],
        'punish_1': info['punish_1'],
        'punish_2': info['punish_2'],
        'punish_3': info['punish_3'],
    }

    if request.method == 'GET':
        rpForm = form_admin.RewardPunishInfoForm(initial=init_data)
        return render(request, 'admin_reward_punish.html',
                      {'user': username, 'rpForm': rpForm, 'user_list': user_list, 'page_info': page_info})

    else:
        rpForm = form_admin.RewardPunishInfoForm(request.POST)

        if rpForm.is_valid():
            reward_1 = rpForm.cleaned_data['reward_1']
            reward_2 = rpForm.cleaned_data['reward_2']
            reward_3 = rpForm.cleaned_data['reward_3']
            punish_1 = rpForm.cleaned_data['punish_1']
            punish_2 = rpForm.cleaned_data['punish_2']
            punish_3 = rpForm.cleaned_data['punish_3']

            web_models.RewardAndPunish.objects.filter(id='1').update(reward_1=reward_1, reward_2=reward_2,
                                                                     reward_3=reward_3, punish_1=punish_1,
                                                                     punish_2=punish_2, punish_3=punish_3)
            return render(request, 'admin_reward_punish.html',
                          {'user': username, 'rpForm': rpForm, 'msg': '修改成功！', 'user_list': user_list,
                           'page_info': page_info})

        return render(request, 'admin_reward_punish.html',
                      {'user': username, 'rpForm': rpForm, 'user_list': user_list, 'page_info': page_info})


def admin_reward_set(request):
    """奖励等级设置"""

    mid = request.POST.get('id')
    str_level = request.POST.get('reward_level')

    level = int(str_level)

    web_models.RewardPunishInfo.objects.filter(user_account_id=mid).update(reward_level=level)
    level_data = web_models.RewardPunishInfo.objects.filter(user_account_id=mid).values('reward_level',
                                                                                        'punish_level').first()
    reward_level = level_data['reward_level']
    punish_level = level_data['punish_level']

    # 对奖惩等级进行抵消
    if reward_level == punish_level:
        reward_level = 0
        punish_level = 0

    elif reward_level > punish_level:
        reward_level -= punish_level
        punish_level = 0

    elif punish_level > reward_level:
        punish_level -= reward_level
        reward_level = 0

    web_models.RewardPunishInfo.objects.filter(user_account_id=mid).update(reward_level=reward_level,
                                                                           punish_level=punish_level)
    return HttpResponse('ok')


def admin_punish_set(request):
    """惩罚等级设置"""

    mid = request.POST.get('id')
    str_level = request.POST.get('punish_level')

    level = int(str_level)

    web_models.RewardPunishInfo.objects.filter(user_account_id=mid).update(punish_level=level)

    level_data = web_models.RewardPunishInfo.objects.filter(user_account_id=mid).values('reward_level',
                                                                                        'punish_level').first()
    reward_level = level_data['reward_level']
    punish_level = level_data['punish_level']

    # 对奖惩等级进行抵消
    if reward_level == punish_level:
        reward_level = 0
        punish_level = 0

    elif reward_level > punish_level:
        reward_level -= punish_level
        punish_level = 0

    elif punish_level > reward_level:
        punish_level -= reward_level
        reward_level = 0

    web_models.RewardPunishInfo.objects.filter(user_account_id=mid).update(reward_level=reward_level,
                                                                           punish_level=punish_level)
    return HttpResponse('ok')


def reset_reward_punish(request):
    time.sleep(1)
    web_models.RewardPunishInfo.objects.all().update(reward_level=0, punish_level=0)
    return redirect('/admin_reward_punish/')


def admin_activity_manage(request):
    """党日活动管理"""
    username = request.user

    current_page = request.GET.get('page')
    all_count = web_models.PartyActivity.objects.all().count()
    page_info = PageInfo(current_page, all_count, 8, '/admin_activity_manage', 5)
    data_activity = web_models.PartyActivity.objects.all().order_by('time')[page_info.start():page_info.end()]

    data_apply = web_models.ApplyInfo.objects.all()

    data_list_apply = []
    for item in data_apply:
        data_list_apply.append([item.activity_id, item.member_id])

    data = []
    for item in data_activity:

        count = 0
        # 提取报名人数
        for row in data_list_apply:
            if item.id == row[0]:
                count += 1

        # 整合活动数据
        data.append(
            {'id': item.id,
             'time': item.time,
             'title': item.title,
             'place': item.place,
             'status': item.status,
             'count': count,
             }
        )

    return render(request, 'admin_activity_manage.html', {'data': data, 'page_info': page_info})


def admin_add_activity(request):
    """新增党日活动"""

    init_form = form_admin.ActivityForm()
    if request.method == 'GET':

        return render(request, 'admin_add_activity.html', {'content_form': init_form})

    else:
        content_form = form_admin.ActivityForm(request.POST)

        if content_form.is_valid():
            title = content_form.cleaned_data['title']
            time = content_form.cleaned_data['time']
            place = content_form.cleaned_data['place']
            content = content_form.cleaned_data['content']

            if title != '' and time != None and place != '' and content != '':
                msg = 'OK'
                web_models.PartyActivity.objects.create(title=title, time=time, place=place, content=content,
                                                        status='报名未开始')

                return render(request, 'admin_add_activity.html', {'content_form': init_form, 'msg': msg})
        else:
            msg = 'Error'

            return render(request, 'admin_add_activity.html', {'content_form': content_form, 'msg': msg})


def admin_edit_activity(request):
    """编辑党日活动"""

    username = request.user

    nid = request.GET.get('nid')
    if request.method == 'GET':
        data = web_models.PartyActivity.objects.filter(id=nid).values('title', 'time', 'place', 'content').first()

        init_data = {
            'title': data['title'],
            'time': data['time'],
            'place': data['place'],
            'content': data['content']
        }
        content_form = form_admin.ActivityForm(initial=init_data)
        return render(request, 'admin_edit_activity.html', {'content_form': content_form})

    else:
        content_form = form_admin.ActivityForm(request.POST)

        if content_form.is_valid():
            title = content_form.cleaned_data['title']
            time = content_form.cleaned_data['time']
            place = content_form.cleaned_data['place']
            content = content_form.cleaned_data['content']

            if title != '' and time != None and place != '' and content != '':
                msg = 'OK'
                web_models.PartyActivity.objects.filter(id=nid).update(title=title, time=time, place=place,
                                                                       content=content)

                return render(request, 'admin_add_activity.html', {'content_form': content_form, 'msg': msg})
        else:
            msg = 'Error'
            return render(request, 'admin_add_activity.html', {'content_form': content_form, 'msg': msg})


def admin_activity_info(request):
    """单个党日活动详情"""

    username = request.user
    nid = request.GET.get('nid')
    data = web_models.PartyActivity.objects.filter(id=nid).first()
    data_apply = web_models.ApplyInfo.objects.filter(activity_id=nid).values('activity_id', 'member_id',
                                                                             'member__member_name').all()
    count = len(data_apply)

    return render(request, 'admin_activity_info.html', {'data': data, 'data_apply': data_apply, 'count': count})


def admin_startapply_activity(request):
    """党日活动启动报名"""

    time.sleep(1)
    nid = request.GET.get('nid')
    web_models.PartyActivity.objects.filter(id=nid).update(status='报名中')

    return redirect('/admin_activity_info/?nid=' + nid)


def admin_endapply_activity(request):
    """党日活动结束报名"""

    time.sleep(1)
    nid = request.GET.get('nid')
    web_models.PartyActivity.objects.filter(id=nid).update(status='报名结束')

    return redirect('/admin_activity_info/?nid=' + nid)


def admin_end_activity(request):
    """党日活动结束"""

    time.sleep(1)
    nid = request.GET.get('nid')
    web_models.PartyActivity.objects.filter(id=nid).update(status='活动已结束')

    return redirect('/admin_activity_info/?nid=' + nid)


def admin_del_activity(request):
    """删除党日活动"""

    time.sleep(2)
    nid = request.GET.get('nid')
    web_models.PartyActivity.objects.filter(id=nid).delete()

    return redirect('/admin_activity_manage/')


def admin_party_build(request):
    """党建管理"""

    return render(request, 'admin_party_build.html')


def admin_member_develop(request):
    """党员发展"""

    username = request.user

    current_page = request.GET.get('page')
    # 获取身份为预备党员且未转出的预备党员数量
    all_count = web_models.Member.objects.filter(member_status='预备党员').exclude(is_out_team='是').all().count()
    page_info = PageInfo(current_page, all_count, 8, '/admin_member_develop', 5)

    # 获取身份为预备党员且未转出的党员
    data_list = web_models.Member.objects.filter(member_status='预备党员').exclude(is_out_team='是').all().order_by(
        'first_date')[page_info.start():page_info.end()]

    regular_date = web_models.DateSet.objects.filter(id=1).values('regular_date_set').first()

    return render(request, 'admin_member_develop.html',
                  {'user': username, 'data_list': data_list, 'page_info': page_info, 'date': regular_date})


def set_member_develop(request):
    """党员发展数据提交"""

    time.sleep(1)

    nid = request.GET.get('nid')
    date = request.GET.get('date')

    web_models.Member.objects.filter(member_id=nid).update(member_status='正式党员', regular_date=date)
    web_models.DateSet.objects.filter(id=1).update(regular_date_set=date)

    return redirect('/admin_member_develop/')


def admin_activist_develop(request):
    """积极分子发展"""

    username = request.user

    current_page = request.GET.get('page')
    all_count = web_models.Activist.objects.filter().all().count()
    page_info = PageInfo(current_page, all_count, 8, '/admin_activist_develop', 5)

    data_list = web_models.Activist.objects.all().order_by('apply_date')[
                page_info.start():page_info.end()]

    first_date = web_models.DateSet.objects.filter(id=1).values('first_date_set').first()

    return render(request, 'admin_activist_develop.html',
                  {'user': username, 'data_list': data_list, 'page_info': page_info, 'date': first_date})


def set_activist_develop(request):
    """积极分子发展数据提交"""

    time.sleep(1)

    nid = request.GET.get('nid')
    username = request.GET.get('user')
    date = request.GET.get('date')

    user = rbac_models.UserProfile.objects.filter(username=username).first()
    data = web_models.Activist.objects.filter(activist_id=nid).first()

    # 为发展为预备党员的积极分子添加党员用户信息
    member = web_models.Member.objects.create(
        member_name=data.activist_name,
        member_gender=data.activist_gender,
        member_phone=data.activist_phone,
        first_date=date,
        member_status='预备党员',
        member_duty='无',
        voluntary_time=data.voluntary_time,
        is_out_team='否',
        user_account=user
    )

    # 删除原积极分子信息
    web_models.Activist.objects.filter(activist_id=nid).delete()

    # 更新原登陆账户的账号类型为党员用户
    rbac_models.UserProfile.objects.filter(username=username).update(roles_id=2)

    # 为新预备党员添加奖惩信息
    web_models.RewardPunishInfo.objects.create(reward_level=0, punish_level=0, user_account=member)

    web_models.DateSet.objects.filter(id=1).update(first_date_set=date)

    return redirect('/admin_activist_develop/')


def admin_member_transfer_out(request):
    """党员转出"""
    username = request.user

    current_page = request.GET.get('page')
    # 获取转出状态为‘转出待确认’的党员数量
    all_count = web_models.Member.objects.filter(is_out_team='转出待确认').all().count()
    page_info = PageInfo(current_page, all_count, 8, '/admin_member_transfer_out', 5)

    # 获取转出状态为‘转出待确认’的党员
    data_list = web_models.Member.objects.filter(is_out_team='转出待确认').all().order_by('first_date')[
                page_info.start():page_info.end()]

    out_date = web_models.DateSet.objects.filter(id=1).values('out_date_set').first()

    return render(request, 'admin_member_transfer_out.html',
                  {'user': username, 'data_list': data_list, 'page_info': page_info, 'date': out_date})


def submit_member_transfer_out(request):
    """党员转出提交"""

    nid = request.GET.get('nid')
    date = request.GET.get('date')

    web_models.Member.objects.filter(member_id=nid).update(is_out_team="是", out_confirm_date=date, member_duty="无")

    return redirect('/admin_member_transfer_out/')


def admin_member_transfer_in(request):
    """党员转入"""

    username = request.user

    in_date = web_models.DateSet.objects.filter(id=1).values('in_date_set').first()

    init_data = {'in_date': in_date['in_date_set']}
    inForm = form_admin.TransferInForm(initial=init_data)

    if request.method == 'GET':

        return render(request, 'admin_member_transfer_in.html',
                      {'user': username, 'transferinForm': inForm})

    else:

        transferinForm = form_admin.TransferInForm(request.POST)

        if transferinForm.is_valid():
            username = transferinForm.cleaned_data['username']
            member_name = transferinForm.cleaned_data['member_name']
            member_gender = transferinForm.cleaned_data['member_gender']
            member_status = transferinForm.cleaned_data['member_status']
            in_date = transferinForm.cleaned_data['in_date']
            come_from_party = transferinForm.cleaned_data['come_from_party']

            # 查找用户名是否已经存在
            exist = rbac_models.UserProfile.objects.filter(username=username).first()

            # 用户名不存在，返回转入成功
            if not exist:
                role = rbac_models.Role.objects.filter(usertype='党员用户').first()
                new_user = rbac_models.UserProfile.objects.create_user(username=username, password=username,
                                                                       roles_id=role.rid)
                # 为转入党员添加账户信息
                member = web_models.Member.objects.create(
                    member_name=member_name,
                    member_gender=member_gender,
                    member_status=member_status,
                    in_date=in_date,
                    member_duty='无',
                    is_out_team='否',
                    come_from_party=come_from_party,
                    user_account=new_user
                )

                info = {'flag': 'ok', 'name': member_name}

                # 为转入党员添加奖惩信息
                web_models.RewardPunishInfo.objects.create(reward_level=0, punish_level=0, user_account=member)

                # 更新转入日期
                web_models.DateSet.objects.filter(id=1).update(in_date_set=in_date)

                return render(request, 'admin_member_transfer_in.html',
                              {'user': username, 'info': info, 'transferinForm': inForm})

            # 用户名存在，返回转入失败
            else:
                info = {'flag': 'exist', 'name': member_name}
                return render(request, 'admin_member_transfer_in.html',
                              {'user': username, 'info': info, 'transferinForm': transferinForm})

        return render(request, 'admin_member_transfer_in.html',
                      {'user': username, 'transferinForm': transferinForm})


def admin_info_manage(request):
    """基本信息管理页面"""

    return render(request, 'admin_info_manage.html')


def admin_party_info_manage(request):
    """组织信息管理页面"""

    username = request.user

    data = web_models.PartyInfo.objects.filter(id=1).first()
    member_list = web_models.Member.objects.filter(is_out_team='否').values('member_id', 'member_name').all().order_by(
        'first_date')

    if request.method == 'GET':

        return render(request, 'admin_party_info_manage.html', {'data': data, 'member_list': member_list})
    else:

        msg = {'tips': '修改失败:', 'name_error': '', 'duty_error': '', 'flag': ''}

        party_name = request.POST.get('party_name')
        party_secretary = request.POST.get('party_secretary')
        party_organizer = request.POST.get('party_organizer')
        party_publicity = request.POST.get('party_publicity')
        party_discipline = request.POST.get('party_discipline')

        check = [party_secretary, party_organizer, party_publicity, party_discipline]

        if len(check) != len(set(check)):
            msg['duty_error'] = '职务任职不能重复'

        # 判断输入的党员职务是否有空的(值为0即为空)
        if '0' in check:
            msg['duty_error'] = '党员职务不能为空'

        # 判断输入的组织名称是否为空
        if party_name == '':
            msg['name_error'] = '组织名称不能为空'

        if msg['name_error'] == '' and msg['duty_error'] == '':
            msg['flag'] = 'ok'

            # 将原来的职务信息清空
            web_models.Member.objects.filter(member_duty='支部书记').update(member_duty='无')
            web_models.Member.objects.filter(member_duty='组织委员').update(member_duty='无')
            web_models.Member.objects.filter(member_duty='宣传委员').update(member_duty='无')
            web_models.Member.objects.filter(member_duty='纪检委员').update(member_duty='无')

            # 更新新的职务信息
            web_models.Member.objects.filter(member_id=party_secretary).update(member_duty='支部书记')
            web_models.Member.objects.filter(member_id=party_organizer).update(member_duty='组织委员')
            web_models.Member.objects.filter(member_id=party_publicity).update(member_duty='宣传委员')
            web_models.Member.objects.filter(member_id=party_discipline).update(member_duty='纪检委员')

            for item in member_list:
                if str(item['member_id']) == str(party_secretary):
                    web_models.PartyInfo.objects.filter(id=1).update(party_secretary=item['member_name'])
                if str(item['member_id']) == str(party_organizer):
                    web_models.PartyInfo.objects.filter(id=1).update(party_organizer=item['member_name'])
                if str(item['member_id']) == str(party_publicity):
                    web_models.PartyInfo.objects.filter(id=1).update(party_publicity=item['member_name'])
                if str(item['member_id']) == str(party_discipline):
                    web_models.PartyInfo.objects.filter(id=1).update(party_discipline=item['member_name'])

            data = web_models.PartyInfo.objects.filter(id=1).first()
            return render(request, 'admin_party_info_manage.html',
                          {'data': data, 'member_list': member_list, 'msg': msg})
        else:

            return render(request, 'admin_party_info_manage.html',
                          {'data': data, 'member_list': member_list, 'msg': msg})


def admin_member_info_manage(request):
    """党员信息管理页面"""

    username = request.user

    current_page = request.GET.get('page')
    # 获取身份为预备党员且未转出的党员数量
    all_count = web_models.Member.objects.exclude(is_out_team='是').all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_member_info_manage', 5)

    data_list = web_models.Member.objects.exclude(is_out_team='是').all().order_by('first_date')[
                page_info.start():page_info.end()]

    return render(request, 'admin_member_info_manage.html', {'data_list': data_list, 'page_info': page_info})


def admin_member_out_info(request):
    """已转出党员信息"""

    username = request.user

    current_page = request.GET.get('page')
    # 获取身份为预备党员且未转出的党员数量
    all_count = web_models.Member.objects.filter(is_out_team='是').all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_member_info_manage', 5)

    data_list = web_models.Member.objects.filter(is_out_team='是').all().order_by('first_date')[
                page_info.start():page_info.end()]

    return render(request, 'admin_member_out_info.html', {'data_list': data_list, 'page_info': page_info})


def admin_member_info_alter(request):
    """党员信息修改"""

    username = request.user

    mid = request.GET.get('mid')

    data_list = web_models.Member.objects.filter(member_id=mid).first()

    init_data = {
        'user_name': data_list.user_account.username,
        'user_type': data_list.user_account.roles.usertype,
        'member_name': data_list.member_name,
        'member_gender': data_list.member_gender,
        'member_phone': data_list.member_phone,
        'member_email': data_list.user_account.email,
        'member_status': data_list.member_status,
        'member_duty': data_list.member_duty,
        'first_date': data_list.first_date,
        'regular_date': data_list.regular_date,
        'voluntary_time': data_list.voluntary_time,
        'come_from_party': data_list.come_from_party,
    }

    initForm = form_admin.MemberInfoForm(initial=init_data)

    if request.method == 'GET':

        return render(request, 'admin_member_info_alter.html', {'data_list': data_list, 'memberinfoForm': initForm})

    else:
        memberinfoForm = form_admin.MemberInfoForm(request.POST)
        data_list = web_models.Member.objects.filter(member_id=mid).first()

        if memberinfoForm.is_valid():
            member_name = memberinfoForm.cleaned_data['member_name']
            member_gender = memberinfoForm.cleaned_data['member_gender']
            member_phone = memberinfoForm.cleaned_data['member_phone']
            member_email = memberinfoForm.cleaned_data['member_email']
            member_status = memberinfoForm.cleaned_data['member_status']
            first_date = memberinfoForm.cleaned_data['first_date']
            regular_date = memberinfoForm.cleaned_data['regular_date']
            voluntary_time = memberinfoForm.cleaned_data['voluntary_time']
            come_from_party = memberinfoForm.cleaned_data['come_from_party']

            if member_status == '预备党员':
                regular_date = None

            # 更新邮箱信息
            rbac_models.UserProfile.objects.filter(member__member_id=mid).update(email=member_email)

            #  更新党员个人信息
            web_models.Member.objects.filter(member_id=mid).update(
                member_name=member_name,
                member_gender=member_gender,
                member_phone=member_phone,
                member_status=member_status,
                first_date=first_date,
                regular_date=regular_date,
                voluntary_time=voluntary_time,
                come_from_party=come_from_party
            )

            data_list = web_models.Member.objects.filter(member_id=mid).first()

            init_data2 = {
                'user_name': data_list.user_account.username,
                'user_type': data_list.user_account.roles.usertype,
                'member_name': data_list.member_name,
                'member_gender': data_list.member_gender,
                'member_phone': data_list.member_phone,
                'member_email': data_list.user_account.email,
                'member_status': data_list.member_status,
                'member_duty': data_list.member_duty,
                'first_date': data_list.first_date,
                'regular_date': data_list.regular_date,
                'voluntary_time': data_list.voluntary_time,
                'come_from_party': data_list.come_from_party,
            }

            memberinfoForm = form_admin.MemberInfoForm(initial=init_data2)

            return render(request, 'admin_member_info_alter.html',
                          {'data_list': data_list, 'memberinfoForm': memberinfoForm, 'msg': '修改成功'})
        else:
            return render(request, 'admin_member_info_alter.html',
                          {'data_list': data_list, 'memberinfoForm': memberinfoForm})


def admin_party_statistics(request):
    """党内统计"""

    time.sleep(0.5)
    meeting_year = datetime.date.today().year
    lecture_year = datetime.date.today().year

    myear = request.GET.get('myear')
    lyear = request.GET.get('lyear')

    if myear != None or lyear != None:
        meeting_year = myear
        lecture_year = lyear

    meeting_year = int(meeting_year)
    lecture_year = int(lecture_year)

    # 获取正式党员人数
    num_official_member = web_models.Member.objects.exclude(is_out_team='是').filter(member_status='正式党员').count()
    # 获取预备党员人数
    num_prepare_member = web_models.Member.objects.exclude(is_out_team='是').filter(member_status='预备党员').count()
    # 获取积极分子人数
    num_activist = web_models.Activist.objects.count()

    # 获取男生党员人数
    num_male_member = web_models.Member.objects.exclude(is_out_team='是').filter(member_gender='男').count()
    # 获取女生党员人数
    num_female_member = web_models.Member.objects.exclude(is_out_team='是').filter(member_gender='女').count()

    # 获取男生积极分子人数
    num_male_activist = web_models.Activist.objects.filter(activist_gender='男').count()
    # 获取女生积极分子人数
    num_female_activist = web_models.Activist.objects.filter(activist_gender='女').count()

    data_num = {
        'num_member': [num_official_member, num_prepare_member],
        'num_member_gender': [num_male_member, num_female_member],

        'num_member_activist': [num_official_member, num_prepare_member, num_activist],
        'num_member_activist_gender': [num_male_member + num_male_activist, num_female_member + num_female_activist]
    }

    # 按月份分组查询会议数据
    meetings = web_models.MeetingRecord.objects.extra(
        select={'month': connections[web_models.MeetingRecord.objects.db].ops.date_trunc_sql('month', 'date')}).values(
        'month').annotate(dcount=Count('date')).order_by('month')

    # 按月份分组查询党课数据
    lectures = web_models.LectureRecord.objects.extra(
        select={'month': connections[web_models.MeetingRecord.objects.db].ops.date_trunc_sql('month', 'date')}).values(
        'month').annotate(dcount=Count('date')).order_by('month')

    data_meeting = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    data_lecture = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    year_meeting = []
    year_lecture = []

    for item in meetings:
        if item['month'].year not in year_meeting:
            year_meeting.append(item['month'].year)

        if item['month'].year == meeting_year:
            if item['month'].month == 1:
                data_meeting[0] += item['dcount']
            if item['month'].month == 2:
                data_meeting[1] += item['dcount']
            if item['month'].month == 3:
                data_meeting[2] += item['dcount']
            if item['month'].month == 4:
                data_meeting[3] += item['dcount']
            if item['month'].month == 5:
                data_meeting[4] += item['dcount']
            if item['month'].month == 6:
                data_meeting[5] += item['dcount']
            if item['month'].month == 7:
                data_meeting[6] += item['dcount']
            if item['month'].month == 8:
                data_meeting[7] += item['dcount']
            if item['month'].month == 9:
                data_meeting[8] += item['dcount']
            if item['month'].month == 10:
                data_meeting[9] += item['dcount']
            if item['month'].month == 11:
                data_meeting[10] += item['dcount']
            if item['month'].month == 12:
                data_meeting[11] += item['dcount']

    for item in lectures:
        if item['month'].year not in year_lecture:
            year_lecture.append(item['month'].year)

        if item['month'].year == lecture_year:
            if item['month'].month == 1:
                data_lecture[0] += item['dcount']
            if item['month'].month == 2:
                data_lecture[1] += item['dcount']
            if item['month'].month == 3:
                data_lecture[2] += item['dcount']
            if item['month'].month == 4:
                data_lecture[3] += item['dcount']
            if item['month'].month == 5:
                data_lecture[4] += item['dcount']
            if item['month'].month == 6:
                data_lecture[5] += item['dcount']
            if item['month'].month == 7:
                data_lecture[6] += item['dcount']
            if item['month'].month == 8:
                data_lecture[7] += item['dcount']
            if item['month'].month == 9:
                data_lecture[8] += item['dcount']
            if item['month'].month == 10:
                data_lecture[9] += item['dcount']
            if item['month'].month == 11:
                data_lecture[10] += item['dcount']
            if item['month'].month == 12:
                data_lecture[11] += item['dcount']

    year_meeting.sort()
    year_lecture.sort()

    try:
        year_meeting.remove(meeting_year)
        year_lecture.remove(lecture_year)
    except:
        pass

    return render(request, 'admin_party_statistics.html',
                  {'meeting_year': meeting_year, 'lecture_year': lecture_year, 'data_meeting': data_meeting,
                   'data_lecture': data_lecture,
                   'data_num': data_num, 'year_meeting': year_meeting, 'year_lecture': year_lecture})


def admin_activist_manage(request):
    """积极分子管理"""

    return render(request, 'admin_activist_manage.html')


def admin_activist_info_manage(request):
    """积极分子信息管理"""
    username = request.user

    current_page = request.GET.get('page')
    # 获取身份为预备党员且未转出的党员数量
    all_count = web_models.Activist.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_activist_info_manage', 5)

    data_list = web_models.Activist.objects.all().order_by('apply_date')[
                page_info.start():page_info.end()]

    return render(request, 'admin_activist_info_manage.html', {'data_list': data_list, 'page_info': page_info})


def admin_activist_info_alter(request):
    """积极分子信息更新"""

    username = request.user

    nid = request.GET.get('nid')

    data_list = web_models.Activist.objects.filter(activist_id=nid).first()

    init_data = {
        'user_name': data_list.user_account.username,
        'user_type': data_list.user_account.roles.usertype,
        'activist_name': data_list.activist_name,
        'activist_gender': data_list.activist_gender,
        'activist_phone': data_list.activist_phone,
        'activist_email': data_list.user_account.email,
        'apply_date': data_list.apply_date,
        'voluntary_time': data_list.voluntary_time,
    }

    initForm = form_admin.ActivistInfoForm(initial=init_data)

    if request.method == 'GET':

        return render(request, 'admin_activist_info_alter.html', {'data_list': data_list, 'activistinfoForm': initForm})

    else:
        activistinfoForm = form_admin.ActivistInfoForm(request.POST)
        data_list = web_models.Activist.objects.filter(activist_id=nid).first()

        if activistinfoForm.is_valid():
            activist_name = activistinfoForm.cleaned_data['activist_name']
            activist_gender = activistinfoForm.cleaned_data['activist_gender']
            activist_phone = activistinfoForm.cleaned_data['activist_phone']
            activist_email = activistinfoForm.cleaned_data['activist_email']
            apply_date = activistinfoForm.cleaned_data['apply_date']
            voluntary_time = activistinfoForm.cleaned_data['voluntary_time']

            # 更新邮箱信息
            rbac_models.UserProfile.objects.filter(activist__activist_id=nid).update(email=activist_email)

            #  更新积极分子个人信息
            web_models.Activist.objects.filter(activist_id=nid).update(
                activist_name=activist_name,
                activist_gender=activist_gender,
                activist_phone=activist_phone,
                apply_date=apply_date,
                voluntary_time=voluntary_time,
            )

            data_list = web_models.Activist.objects.filter(activist_id=nid).first()

            init_data2 = {
                'user_name': data_list.user_account.username,
                'user_type': data_list.user_account.roles.usertype,
                'activist_name': data_list.activist_name,
                'activist_gender': data_list.activist_gender,
                'activist_phone': data_list.activist_phone,
                'activist_email': data_list.user_account.email,
                'apply_date': data_list.apply_date,
                'voluntary_time': data_list.voluntary_time,
            }

            activistinfoForm = form_admin.ActivistInfoForm(initial=init_data2)

            return render(request, 'admin_activist_info_alter.html',
                          {'data_list': data_list, 'activistinfoForm': activistinfoForm, 'msg': '修改成功'})
        else:
            return render(request, 'admin_activist_info_alter.html',
                          {'data_list': data_list, 'activistinfoForm': activistinfoForm})


def admin_member_add(request):
    """成员添加"""

    username = request.user

    addmemberForm = form_admin.AddMemberForm()

    if request.method == 'GET':

        return render(request, 'admin_member_add.html',
                      {'user': username, 'addmemberForm': addmemberForm})

    else:

        addmemberForm = form_admin.AddMemberForm(request.POST)

        if addmemberForm.is_valid():
            username = addmemberForm.cleaned_data['username']
            add_name = addmemberForm.cleaned_data['add_name']
            add_gender = addmemberForm.cleaned_data['add_gender']
            add_status = addmemberForm.cleaned_data['add_status']

            # 查找用户名是否已经存在
            exist = rbac_models.UserProfile.objects.filter(username=username).first()

            # 用户名不存在，返回转入成功
            if not exist:

                # 添加积极分子
                if add_status == '积极分子':

                    role = rbac_models.Role.objects.filter(usertype='积极分子').first()
                    new_user = rbac_models.UserProfile.objects.create_user(username=username, password=username,
                                                                           roles_id=role.rid)
                    # 为新积极分子添加账户信息
                    activist = web_models.Activist.objects.create(
                        activist_name=add_name,
                        activist_gender=add_gender,
                        user_account=new_user
                    )

                    info = {'flag': 'ok', 'name': add_name}

                    return render(request, 'admin_member_transfer_in.html',
                                  {'user': username, 'info': info, 'addmemberForm': addmemberForm})


                # 添加党员用户
                else:

                    role = rbac_models.Role.objects.filter(usertype='党员用户').first()
                    new_user = rbac_models.UserProfile.objects.create_user(username=username, password=username,
                                                                           roles_id=role.rid)
                    # 为新党员添加账户信息
                    member = web_models.Member.objects.create(
                        member_name=add_name,
                        member_gender=add_gender,
                        member_status=add_gender,
                        member_duty='无',
                        is_out_team='否',
                        user_account=new_user
                    )

                    info = {'flag': 'ok', 'name': add_name}

                    # 为新党员添加奖惩信息
                    web_models.RewardPunishInfo.objects.create(reward_level=0, punish_level=0, user_account=member)

                    return render(request, 'admin_member_add.html',
                                  {'user': username, 'info': info, 'addmemberForm': addmemberForm})

            # 用户名存在，返回转入失败
            else:
                info = {'flag': 'exist', 'name': add_name}
                return render(request, 'admin_member_add.html',
                              {'user': username, 'info': info, 'addmemberForm': addmemberForm})

        return render(request, 'admin_member_add.html',
                      {'user': username, 'addmemberForm': addmemberForm})


def admin_system_maintain(request):
    """系统维护"""

    return render(request, 'admin_system_maintain.html')


def admin_pwd_reset(request):
    """重置密码"""

    username = request.user

    return render(request, 'admin_pwd_reset.html', {'username': username})


def admin_get_one_info(request):
    """获取用户信息"""
    name = request.GET.get('name')
    usertype = request.GET.get('usertype')

    data_list = []

    if usertype == '党员用户':
        data = web_models.Member.objects.filter(user_account__username=name).values('user_account_id', 'member_name',
                                                                                    'member_gender',
                                                                                    'user_account__email',
                                                                                    'member_phone').first()
        if data:
            data_list.append({
                'id': data['user_account_id'],
                'username': name,
                'type': usertype,
                'gender': data['member_gender'],
                'name': data['member_name'],
                'email': data['user_account__email'],
                'phone': data['member_phone'],
                'flag': True
            })
        else:
            data_list.append({
                'flag': None
            })
    elif usertype == '积极分子':
        data = web_models.Activist.objects.filter(user_account__username=name).values('user_account_id','activist_name',
                                                                                      'activist_gender',
                                                                                      'user_account__email',
                                                                                      'activist_phone').first()
        if data:
            data_list.append({
                'id': data['user_account_id'],
                'username': name,
                'type': usertype,
                'name': data['activist_name'],
                'gender': data['activist_gender'],
                'email': data['user_account__email'],
                'phone': data['activist_phone'],
                'flag': True
            })
        else:
            data_list.append({
                'flag': None
            })

    else:
        data_list.append({
            'flag': None
        })

    return HttpResponse(json.dumps(data_list, cls=DateEncoder))


def admin_pwd_reset_submit(request):
    """重置密码提交"""

    ret = {'status': True, 'msg': None}

    uid = request.POST.get('id')
    username = request.POST.get('username')

    try:
        user = rbac_models.UserProfile.objects.filter(uid=uid).first()
        user.set_password(username)
        user.save()
    except:
        ret['status'] = False
        ret['msg'] = '失败！'

    return HttpResponse(json.dumps(ret))


def admin_activist_meeting_record(request):
    """会议记录页面"""

    username = request.user
    # 获取第几页
    current_page = request.GET.get('page')
    # 获取数据总条数
    all_count = web_models.ActivistMeetingRecord.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_meeting_record', 5)

    # 按照date排序读取数据
    data = web_models.ActivistMeetingRecord.objects.all().order_by('date')[page_info.start():page_info.end()]

    for row in data:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    return render(request, 'admin_activist_meeting_record.html',
                  {'user': username, 'data': data, 'page_info': page_info})


def activist_get_all_activist(request):
    """获取全部积极分子信息"""

    time.sleep(0.5)

    temp_list = web_models.Activist.objects.all()
    activist_list = []
    for item in temp_list:
        activist_list.append({'id': item.activist_id, 'activist_name': item.activist_name})

    return HttpResponse(json.dumps(activist_list))


def activist_get_one_meeting(request):
    """获取一个会议信息"""

    time.sleep(0.5)

    uid = request.GET.get('id')
    data = web_models.ActivistMeetingRecord.objects.filter(id=uid).first()

    member = web_models.Activist.objects.all()
    member_list = []
    for item in member:
        member_list.append(item.activist_name)

    data_list = []
    data_list.append({
        'id': data.id,
        'date': data.date,
        'place': data.place,
        'title': data.title,
        'member': member_list,
        'attendance': eval(data.attendance),
        'absence': eval(data.absence),
    })

    # 删除member中存在的attendance
    for item in data_list[0]['attendance']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    # 删除member中存在的absence
    for item in data_list[0]['absence']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    return HttpResponse(json.dumps(data_list, cls=DateEncoder))


def activist_set_meeting_record(request):
    """添加和修改会议信息"""

    ret = {'status': True, 'msg': None}

    nid = request.POST.get('id')
    date = request.POST.get('date')
    place = request.POST.get('place')
    flag = request.POST.get('flag')
    title = request.POST.get('title')
    attend_list = request.POST.getlist('attend_list')
    absent_list = request.POST.getlist('absent_list')

    if date == '' or title == '' or place == '' or attend_list == ['']:
        ret['status'] = False
        ret['msg'] = '输入信息有误，请重新输入！'
        return HttpResponse(json.dumps(ret))

    else:
        attend_num = len(attend_list)

        if absent_list == ['']:
            absent_num = 0
        else:
            absent_num = len(absent_list)

        # 添加会议
        if flag == 'add':
            web_models.ActivistMeetingRecord.objects.create(date=date, place=place, title=title, attend_num=attend_num,
                                                            absent_num=absent_num, attendance=attend_list,
                                                            absence=absent_list)
        # 修改会议
        else:
            web_models.ActivistMeetingRecord.objects.filter(id=nid).update(date=date, place=place, title=title,
                                                                           attend_num=attend_num,
                                                                           absent_num=absent_num,
                                                                           attendance=attend_list,
                                                                           absence=absent_list)

        return HttpResponse(json.dumps(ret))


def activist_del_one_meeting(request):
    """删除一个会议"""

    time.sleep(2)

    nid = request.GET.get('nid')

    web_models.ActivistMeetingRecord.objects.filter(id=nid).delete()

    return redirect('/admin_activist_meeting_record/')


def admin_activist_lecture_record(request):
    """党课记录页面"""

    username = request.user
    # 获取第几页
    current_page = request.GET.get('page')
    # 获取数据总条数
    all_count = web_models.ActivistLectureRecord.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/admin_activist_lecture_record', 5)

    # 按照date排序读取数据
    data = web_models.ActivistLectureRecord.objects.all().order_by('date')[page_info.start():page_info.end()]

    for row in data:
        row.attendance = eval(row.attendance)
        row.absence = eval(row.absence)

    return render(request, 'admin_activist_lecture_record.html',
                  {'user': username, 'data': data, 'page_info': page_info})


def activist_get_one_lecture(request):
    """获取一个党课信息"""

    time.sleep(0.5)

    uid = request.GET.get('id')
    data = web_models.ActivistLectureRecord.objects.filter(id=uid).first()

    member = web_models.Activist.objects.all()
    member_list = []
    for item in member:
        member_list.append(item.activist_name)

    data_list = []
    data_list.append({
        'id': data.id,
        'date': data.date,
        'place': data.place,
        'title': data.title,
        'member': member_list,
        'attendance': eval(data.attendance),
        'absence': eval(data.absence),
    })

    # 删除member中存在的attendance
    for item in data_list[0]['attendance']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    # 删除member中存在的absence
    for item in data_list[0]['absence']:
        if item in data_list[0]['member']:
            data_list[0]['member'].remove(item)

    return HttpResponse(json.dumps(data_list, cls=DateEncoder))


def activist_set_lecture_record(request):
    """添加和修改党课信息"""

    ret = {'status': True, 'msg': None}

    nid = request.POST.get('id')
    date = request.POST.get('date')
    place = request.POST.get('place')
    flag = request.POST.get('flag')
    title = request.POST.get('title')
    attend_list = request.POST.getlist('attend_list')
    absent_list = request.POST.getlist('absent_list')

    if date == '' or title == '' or place == '' or attend_list == ['']:
        ret['status'] = False
        ret['msg'] = '输入信息有误，请重新输入！'
        return HttpResponse(json.dumps(ret))

    else:
        attend_num = len(attend_list)

        if absent_list == ['']:
            absent_num = 0
        else:
            absent_num = len(absent_list)

        # 添加会议
        if flag == 'add':
            web_models.ActivistLectureRecord.objects.create(date=date, place=place, title=title, attend_num=attend_num,
                                                            absent_num=absent_num, attendance=attend_list,
                                                            absence=absent_list)
        # 修改会议
        else:
            web_models.ActivistLectureRecord.objects.filter(id=nid).update(date=date, place=place, title=title,
                                                                           attend_num=attend_num,
                                                                           absent_num=absent_num,
                                                                           attendance=attend_list,
                                                                           absence=absent_list)
        return HttpResponse(json.dumps(ret))


def activist_del_one_lecture(request):
    """删除一个党课"""

    time.sleep(2)
    nid = request.GET.get('nid')
    web_models.ActivistLectureRecord.objects.filter(id=nid).delete()

    return redirect('/admin_activist_lecture_record/')
