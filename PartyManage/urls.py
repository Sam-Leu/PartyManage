"""PartyManage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.urls import include
from django import views

from web.views import view_admin
from web.views import view_activist
from web.views import view_member
from web.views import view_account
import web

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # 插件模块等
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('ueditor/', include('DjangoUeditor.urls')),

    # 登陆相关
    url(r'^login/$', view_account.login),
    url(r'^logout/$', view_account.logout),

    ########## 管理员端 ##########

    # 首页
    url(r'^admin_index/$', view_admin.admin_index),

    # 个人信息相关
    url(r'^admin_profile/$', view_admin.admin_profile),
    url(r'^admin_addinfo/$', view_admin.admin_addinfo),
    url(r'^admin_profile_alter/$', view_admin.admin_profile_alter),
    url(r'^admin_pwd_alter/$', view_admin.admin_pwd_alter),

    # 党务管理相关
    url(r'^admin_party_affairs/$', view_admin.admin_party_affairs),

    url(r'^admin_meeting_record/$', view_admin.admin_meeting_record),
    url(r'^get_all_member/$', view_admin.get_all_member),
    url(r'^get_one_meeting/$', view_admin.get_one_meeting),
    url(r'^set_meeting_record/$', view_admin.set_meeting_record),
    url(r'^del_one_meeting/$', view_admin.del_one_meeting),

    url(r'^admin_lecture_record/$', view_admin.admin_lecture_record),
    url(r'^get_one_lecture/$', view_admin.get_one_lecture),
    url(r'^set_lecture_record/$', view_admin.set_lecture_record),
    url(r'^del_one_lecture/$', view_admin.del_one_lecture),

    url(r'^admin_reward_punish/$', view_admin.admin_reward_punish),
    url(r'^admin_reward_set/$', view_admin.admin_reward_set),
    url(r'^admin_punish_set/$', view_admin.admin_punish_set),
    url(r'^reset_reward_punish/$', view_admin.reset_reward_punish),
    url(r'^admin_activity_manage/$', view_admin.admin_activity_manage),
    url(r'^admin_add_activity/$', view_admin.admin_add_activity),
    url(r'^admin_edit_activity/$', view_admin.admin_edit_activity),
    url(r'^admin_activity_info/$', view_admin.admin_activity_info),
    url(r'^admin_startapply_activity/$', view_admin.admin_startapply_activity),
    url(r'^admin_endapply_activity/$', view_admin.admin_endapply_activity),
    url(r'^admin_end_activity/$', view_admin.admin_end_activity),
    url(r'^admin_del_activity/$', view_admin.admin_del_activity),

    # 党建管理相关
    url(r'^admin_party_build/$', view_admin.admin_party_build),
    url(r'^admin_member_develop/$', view_admin.admin_member_develop),
    url(r'^set_member_develop/$', view_admin.set_member_develop),
    url(r'^admin_activist_develop/$', view_admin.admin_activist_develop),
    url(r'^set_activist_develop/$', view_admin.set_activist_develop),
    url(r'^admin_member_transfer_out/$', view_admin.admin_member_transfer_out),
    url(r'^submit_member_transfer_out/$', view_admin.submit_member_transfer_out),
    url(r'^admin_member_transfer_in/$', view_admin.admin_member_transfer_in),

    # 基本信息管理相关
    url(r'^admin_info_manage/$', view_admin.admin_info_manage),
    url(r'^admin_party_info_manage/$', view_admin.admin_party_info_manage),
    url(r'^admin_member_info_manage/$', view_admin.admin_member_info_manage),
    url(r'^admin_member_out_info/$', view_admin.admin_member_out_info),
    url(r'^admin_member_info_alter/$', view_admin.admin_member_info_alter),

    # 党内统计
    url(r'^admin_party_statistics/$', view_admin.admin_party_statistics),

    # 积极分子信息管理
    url(r'^admin_activist_manage/$', view_admin.admin_activist_manage),
    url(r'^admin_activist_info_manage/$', view_admin.admin_activist_info_manage),
    url(r'^admin_activist_info_alter/$', view_admin.admin_activist_info_alter),

    url(r'^admin_activist_meeting_record/$', view_admin.admin_activist_meeting_record),
    url(r'^activist_get_all_activist/$', view_admin.activist_get_all_activist),
    url(r'^activist_get_one_meeting/$', view_admin.activist_get_one_meeting),
    url(r'^activist_set_meeting_record/$', view_admin.activist_set_meeting_record),
    url(r'^activist_del_one_meeting/$', view_admin.activist_del_one_meeting),

    url(r'^admin_activist_lecture_record/$', view_admin.admin_activist_lecture_record),
    url(r'^activist_get_one_lecture/$', view_admin.activist_get_one_lecture),
    url(r'^activist_set_lecture_record/$', view_admin.activist_set_lecture_record),
    url(r'^activist_del_one_lecture/$', view_admin.activist_del_one_lecture),

    # 系统维护相关
    url(r'^admin_system_maintain/$', view_admin.admin_system_maintain),
    url(r'^admin_member_add/$', view_admin.admin_member_add),
    url(r'^admin_pwd_reset/$', view_admin.admin_pwd_reset),
    url(r'^admin_get_one_info/$', view_admin.admin_get_one_info),
    url(r'^admin_pwd_reset_submit/$', view_admin.admin_pwd_reset_submit),

    ########## 党员用户端 ##########

    url(r'^member_index/$', view_member.member_index),
    url(r'^member_profile/$', view_member.member_profile),
    url(r'^member_addinfo/$', view_member.member_addinfo),
    url(r'^member_profile_alter/$', view_member.member_profile_alter),
    url(r'^member_pwd_alter/$', view_member.member_pwd_alter),

    url(r'^member_my_meeting/$', view_member.member_my_meeting),

    url(r'^member_my_lecture/$', view_member.member_my_lecture),

    url(r'^member_activity_list/$', view_member.member_activity_list),
    url(r'^member_activity_info/$', view_member.member_activity_info),
    url(r'^member_activity_confirm_apply/$', view_member.member_activity_confirm_apply),
    url(r'^member_activity_cancel_apply/$', view_member.member_activity_cancel_apply),

    url(r'^member_my_reward_punish/$', view_member.member_my_reward_punish),

    url(r'^member_transfer/$', view_member.member_transfer),
    url(r'^member_transfer_submit/$', view_member.member_transfer_submit),
    url(r'^member_transfer_cancel/$', view_member.member_transfer_cancel),

    ########## 积极分子端 ##########

    url(r'^activist_index/$', view_activist.activist_index),

    url(r'^activist_profile/$', view_activist.activist_profile),
    url(r'^activist_addinfo/$', view_activist.activist_addinfo),
    url(r'^activist_profile_alter/$', view_activist.activist_profile_alter),
    url(r'^activist_pwd_alter/$', view_activist.activist_pwd_alter),

    url(r'^activist_my_meeting/$', view_activist.activist_my_meeting),

    url(r'^activist_my_lecture/$', view_activist.activist_my_lecture),

    url(r'^static/(?P<path>.*)$', views.static.serve,{'document_root': settings.STATIC_ROOT}),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
