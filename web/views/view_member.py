#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 17:23

from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rbac import models as rbac_models
from web import models as web_models
from web.forms import form_member
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


def member_index(request):
    username = request.user
    # 提取新用户识别字段
    is_new_user = rbac_models.UserProfile.objects.filter(username=username).values('is_newuser').first()
    flag = is_new_user['is_newuser']

    # 如果是新用户，则需要完善个人信息
    if flag:
        return render(request, 'member_index.html', {'user': username, 'flag': True})
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

        return render(request, 'member_index.html', context)


def member_profile(request):
    """个人信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Admin中的数据
    data_member = web_models.Member.objects.filter(user_account_id=data_profile['uid']).first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_member.member_name,
        'usertype': data_profile['roles__usertype'],
        'gender': data_member.member_gender,
        'email': data_profile['email'],
        'phone': data_member.member_phone,
        'first_date': data_member.first_date,
        'member_status': data_member.member_status,
        'regular_date': data_member.regular_date,
        'member_duty': data_member.member_duty,
        'voluntary_time': data_member.voluntary_time,
        'in_date': data_member.in_date,
        'come_from_party': data_member.come_from_party,
        'out_confirm_date': data_member.out_confirm_date,
        'is_out_team': data_member.is_out_team,
        'leave_to_party': data_member.leave_to_party,

    }

    return render(request, 'member_profile.html', {'user': username, 'data_list': data_list})


def member_addinfo(request):
    """"新用户完善信息页"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'roles__usertype',
                                                                                    'is_newuser', 'member__member_name',
                                                                                    'member__member_gender',
                                                                                    'member__member_status').first()
    data_list = {
        'username': username,
        'usertype': data_profile['roles__usertype'],
        'member_name': data_profile['member__member_name'],
        'member_gender': data_profile['member__member_gender'],
        'member_status': data_profile['member__member_status'],
    }

    # 如果不是新用户
    if not data_profile['is_newuser']:
        tag = True
        return render(request, 'member_addinfo.html', {'user': username, 'tag': tag})

    if request.method == 'GET':

        addinfoForm = form_member.InfoForm()

        return render(request, 'member_addinfo.html',
                      {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})

    else:
        addinfoForm = form_member.InfoForm(request.POST)

        if addinfoForm.is_valid():
            member_email = addinfoForm.cleaned_data['member_email']
            member_phone = addinfoForm.cleaned_data['member_phone']
            first_date = addinfoForm.cleaned_data['first_date']
            regular_date = addinfoForm.cleaned_data['regular_date']
            voluntary_time = addinfoForm.cleaned_data['voluntary_time']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=member_email, is_newuser=0)
            # 更新Admin信息
            web_models.Member.objects.filter(user_account__username=username).update(member_phone=member_phone,
                                                                                     first_date=first_date,
                                                                                     regular_date=regular_date,
                                                                                     voluntary_time=voluntary_time)
            flag = True

            return render(request, 'member_addinfo.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'addinfoForm': addinfoForm})

        else:
            return render(request, 'member_addinfo.html',
                          {'user': username, 'data_list': data_list, 'addinfoForm': addinfoForm})


def member_profile_alter(request):
    """修改个人信息"""

    username = request.user

    # 查找UserProfile中的数据
    data_profile = rbac_models.UserProfile.objects.filter(username=username).values('uid', 'email',
                                                                                    'roles__usertype').first()
    # 查找Admin中的数据
    data_member = web_models.Member.objects.filter(user_account_id=data_profile['uid']).first()
    # 合并数据
    data_list = {
        'username': username,
        'truename': data_member.member_name,
        'usertype': data_profile['roles__usertype'],
        'gender': data_member.member_gender,
        'email': data_profile['email'],
        'phone': data_member.member_phone,
        'first_date': data_member.first_date,
        'member_status': data_member.member_status,
        'regular_date': data_member.regular_date,
        'member_duty': data_member.member_duty,
        'voluntary_time': data_member.voluntary_time,
        'in_date': data_member.in_date,
        'come_from_party': data_member.come_from_party,
        'out_confirm_date': data_member.out_confirm_date,
        'is_out_team': data_member.is_out_team,
        'leave_to_party': data_member.leave_to_party,

    }

    init_data = {
        'member_name': data_member.member_name,
        'member_gender': data_member.member_gender,
        'member_email': data_profile['email'],
        'member_phone': data_member.member_phone,
        'first_date': data_member.first_date,
        'voluntary_time': data_member.voluntary_time,
    }

    if request.method == 'GET':

        alterinfoForm = form_member.EditInfoForm(initial=init_data)

        return render(request, 'member_profile_alter.html',
                      {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})

    else:

        alterinfoForm = form_member.EditInfoForm(request.POST)

        if alterinfoForm.is_valid():
            member_name = alterinfoForm.cleaned_data['member_name']
            member_gender = alterinfoForm.cleaned_data['member_gender']
            member_email = alterinfoForm.cleaned_data['member_email']
            member_phone = alterinfoForm.cleaned_data['member_phone']
            first_date = alterinfoForm.cleaned_data['first_date']
            voluntary_time = alterinfoForm.cleaned_data['voluntary_time']

            # 更新UserProfile信息
            rbac_models.UserProfile.objects.filter(username=username).update(email=member_email)
            # 更新Member信息
            web_models.Member.objects.filter(user_account_id=data_profile['uid']).update(member_name=member_name,
                                                                                         member_gender=member_gender,
                                                                                         member_phone=member_phone,
                                                                                         first_date=first_date,
                                                                                         voluntary_time=voluntary_time)
            flag = True
            return render(request, 'member_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'flag': flag, 'alterinfoForm': alterinfoForm})

        else:
            return render(request, 'member_profile_alter.html',
                          {'user': username, 'data_list': data_list, 'alterinfoForm': alterinfoForm})


@login_required
def member_pwd_alter(request):
    """修改用户密码"""

    username = request.user

    if request.method == 'GET':
        pwdForm = form_account.PwdForm()
        return render(request, 'member_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})

    else:

        pwdForm = form_account.PwdForm(request.POST)
        if pwdForm.is_valid():
            old_password = pwdForm.cleaned_data['old_password']
            new_password = pwdForm.cleaned_data['new_password']
            repeat_password = pwdForm.cleaned_data['repeat_password']

            status = view_account.set_password(request, old_password, new_password, repeat_password)

            if status == 'password_error':
                return render(request, 'member_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '原密码输入错误!'})

            elif status == 'repeat_error':
                return render(request, 'member_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '两次新密码输入不一致!'})

            else:
                logout(request)
                return render(request, 'member_pwd_alter.html',
                              {'user': username, 'pwdForm': pwdForm, 'msg': '修改成功，请重新登录!'})

        else:
            return render(request, 'member_pwd_alter.html', {'user': username, 'pwdForm': pwdForm})


def member_my_meeting(request):
    """我的会议"""

    username = request.user

    name = web_models.Member.objects.filter(user_account__username=username).values('member_name').first()
    data_meeting = web_models.MeetingRecord.objects.all().order_by('date')

    data_list_attend = []
    for item in data_meeting:
        attendance = eval(item.attendance)
        if name['member_name'] in attendance:
            data_list_attend.append(item)

    data_list_absent = []
    for item in data_meeting:
        attendance = eval(item.absence)
        if name['member_name'] in attendance:
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

    return render(request, 'member_my_meeting.html',
                  {'count': count, 'data_list_attend': data_list_attend, 'data_list_absent': data_list_absent})


def member_my_lecture(request):
    """我的党课"""

    username = request.user

    name = web_models.Member.objects.filter(user_account__username=username).values('member_name').first()
    data_meeting = web_models.LectureRecord.objects.all().order_by('date')

    data_list_attend = []
    for item in data_meeting:
        attendance = eval(item.attendance)
        if name['member_name'] in attendance:
            data_list_attend.append(item)

    data_list_absent = []
    for item in data_meeting:
        attendance = eval(item.absence)
        if name['member_name'] in attendance:
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

    return render(request, 'member_my_lecture.html',
                  {'count': count, 'data_list_attend': data_list_attend, 'data_list_absent': data_list_absent})


def member_activity_list(request):
    """党日活动"""

    username = request.user

    current_page = request.GET.get('page')
    all_count = web_models.PartyActivity.objects.all().count()
    page_info = PageInfo(current_page, all_count, 9, '/member_activity_list', 5)

    data_member = web_models.Member.objects.filter(user_account__username=username).values('member_id').first()
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
        # 提取该活动的登陆用户的报名状态
        if [item.id, data_member['member_id']] in data_list_apply:
            apply_status = '已报名'
        else:
            apply_status = '未报名'

        # 整合活动数据
        data.append(
            {'id': item.id,
             'time': item.time,
             'title': item.title,
             'place': item.place,
             'status': item.status,
             'count': count,
             'apply_status': apply_status
             }
        )

    return render(request, 'member_activity_list.html',
                  {'data': data, 'data_member': data_member, 'data_list_apply': data_list_apply,
                   'page_info': page_info})


def member_activity_info(request):
    """党日活动详情"""

    username = request.user
    nid = request.GET.get('nid')
    data_member = web_models.Member.objects.filter(user_account__username=username).values('member_id').first()
    data_temp = web_models.PartyActivity.objects.all().order_by('time')
    data_activity = web_models.PartyActivity.objects.filter(id=nid).first()
    data_apply = web_models.ApplyInfo.objects.filter(activity_id=nid).values('activity_id', 'member_id',
                                                                             'member__member_name').all()
    data_list_apply = []
    for item in data_apply:
        data_list_apply.append([item['activity_id'], item['member_id']])

    for item in data_temp:
        # 提取该活动的登陆用户的报名状态
        if [item.id, data_member['member_id']] in data_list_apply:
            apply_status = '已报名'
            break
        else:
            apply_status = '未报名'

    # 报名人数和报名状态
    infos = {
        'count': len(data_apply),
        'apply_status': apply_status
    }

    return render(request, 'member_activity_info.html',
                  {'data': data_activity, 'data_apply': data_apply, 'infos': infos, 'data_member': data_member})


def member_activity_confirm_apply(request):
    """党日活动报名"""

    aid = request.GET.get('aid')
    mid = request.GET.get('mid')
    web_models.ApplyInfo.objects.create(activity_id=aid, member_id=mid)

    return redirect('/member_activity_info/?nid=' + aid)


def member_activity_cancel_apply(request):
    """党日活动取消报名"""

    aid = request.GET.get('aid')
    mid = request.GET.get('mid')
    web_models.ApplyInfo.objects.filter(activity_id=aid, member_id=mid).delete()

    return redirect('/member_activity_info/?nid=' + aid)


def member_my_reward_punish(request):
    """我的奖惩"""

    username = request.user

    data_reward_punish = web_models.RewardAndPunish.objects.filter(id=1).first()
    data_info = web_models.RewardPunishInfo.objects.filter(user_account__user_account__username=username).first()

    return render(request, 'member_my_reward_punish.html',
                  {'data_reward_punish': data_reward_punish, 'data_info': data_info})


def member_transfer(request):
    """关系转移"""

    username = request.user

    data = web_models.Member.objects.filter(user_account__username=username).values('member_id', 'is_out_team',
                                                                                    'leave_to_party',
                                                                                    'out_confirm_date').first()

    return render(request, 'member_transfer.html', {'data': data})


def member_transfer_submit(request):
    """申请转出提交"""

    time.sleep(3)
    mid = request.GET.get('mid')
    party = request.GET.get('party')

    web_models.Member.objects.filter(member_id=mid).update(is_out_team='转出待确认', leave_to_party=party)

    return redirect('/member_transfer/')


def member_transfer_cancel(request):
    """撤回转出申请"""

    time.sleep(3)
    mid = request.GET.get('mid')

    web_models.Member.objects.filter(member_id=mid).update(is_out_team='否', leave_to_party='')

    return redirect('/member_transfer/')
