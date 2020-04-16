#!/usr/bin/env python
# Author: one
# Date: 2020/3/25
# Time: 15:40


from django.conf import settings
from rbac import models as rbac_models
from web import models as web_models
import datetime

def alter_on_time():
    """定时修改数据库的数据"""

    today = datetime.date.today()
    datas = web_models.Member.objects.filter(is_out_team='是')

    for item in datas:
        confirm_date = item.out_confirm_date
        uid = item.user_account_id

        if today - confirm_date >= settings.CONFIRM_DELETE_DAYS:
            # 将转出的党员用户账号设置为不可登陆，但是不会删除账号
            rbac_models.UserProfile.objects.filter(uid=uid).update(is_active=0)

            print("已禁止登陆的党员:" + item.member_name)






