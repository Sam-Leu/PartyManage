from django.db import models
from rbac.models import UserProfile
from DjangoUeditor3.DjangoUeditor.models import UEditorField


# Create your models here.

class Admin(models.Model):
    """党务管理员信息表"""

    admin_id = models.AutoField(verbose_name='党务管理员id编号', primary_key=True)
    admin_name = models.CharField(verbose_name='党务管理员姓名', max_length=32)
    admin_gender_choices = (('男', "男"), ('女', "女"))
    admin_gender = models.CharField(verbose_name='党务管理员性别', choices=admin_gender_choices, max_length=32)
    admin_phone = models.CharField(verbose_name='党务管理员手机号码', max_length=32)
    user_account = models.OneToOneField(verbose_name='党务管理员对应账号信息外键', to=UserProfile, on_delete=models.CASCADE,
                                        default='')


class Member(models.Model):
    """党员用户信息表"""

    member_id = models.AutoField(verbose_name='党员用户id编号', primary_key=True)
    member_name = models.CharField(verbose_name='党员用户姓名', max_length=32)
    member_gender_choices = (('男', "男"), ('女', "女"))
    member_gender = models.CharField(verbose_name='党员用户性别', choices=member_gender_choices, max_length=32)
    member_phone = models.BigIntegerField(verbose_name='党员用户手机号码', null=True, blank=True)
    first_date = models.DateField(verbose_name='入党日期', null=True, blank=True)
    member_status_choices = (('正式党员', "正式党员"), ('预备党员', "预备党员"))
    member_status = models.CharField(verbose_name='政治面貌', choices=member_status_choices, max_length=32)
    # ：null代表未转正
    regular_date = models.DateField(verbose_name='转正日期', null=True, blank=True)
    member_duty_choices = (('无', "无"), ('支部书记', "支部书记"), ('组织委员', "组织委员"), ('宣传委员', "宣传委员"), ('纪检委员', "纪检委员"))
    member_duty = models.CharField(verbose_name='党员职务', choices=member_duty_choices, max_length=32, null=True,
                                   blank=True)
    voluntary_time = models.IntegerField(verbose_name='志愿时长', null=True, blank=True)
    # ：null代表没有转入操作
    in_date = models.DateField(verbose_name='转入时间', null=True, blank=True)
    come_from_party = models.CharField(verbose_name='转入自什么组织', max_length=128, null=True, blank=True)
    out_confirm_date = models.DateField(verbose_name='转出确认时间', null=True, blank=True)
    is_out_team_choices = (('是', "是"), ('否', "否"), ('转出待确认', "转出待确认"))
    is_out_team = models.CharField(verbose_name='是否完成关系转出', choices=is_out_team_choices, max_length=32)
    leave_to_party = models.CharField(verbose_name='转出到什么组织', max_length=128, null=True, blank=True)
    user_account = models.OneToOneField(verbose_name='党员用户对应账号信息外键', to=UserProfile, on_delete=models.CASCADE,
                                        default='')


class Activist(models.Model):
    """积极分子信息表"""

    activist_id = models.AutoField(verbose_name='积极分子用户id编号', primary_key=True)
    activist_name = models.CharField(verbose_name='积极分子姓名', max_length=32)
    activist_gender_choices = (('男', "男"), ('女', "女"))
    activist_gender = models.CharField(verbose_name='积极分子性别', choices=activist_gender_choices, max_length=32)
    activist_phone = models.BigIntegerField(verbose_name='积极分子手机号码')
    apply_date = models.DateField(verbose_name='积极分子申请入党日期')
    voluntary_time = models.IntegerField(verbose_name='志愿时长', null=True, blank=True)
    user_account = models.OneToOneField(verbose_name='积极分子用户对应账号信息外键', to=UserProfile, on_delete=models.CASCADE,
                                        default='')


class PartyActivity(models.Model):
    """党日活动表"""

    title = models.CharField(verbose_name='活动主题', max_length=128)
    time = models.DateField(verbose_name='活动日期')
    place = models.CharField(verbose_name='活动地点', max_length=32)
    content = UEditorField(u'内容', toolbars="full", imagePath="", filePath="",
                           upload_settings={"imageMaxSize": 1204000},
                           settings={}, command=None, blank=True)
    apply_begin = models.DateField(verbose_name='活动报名起始日期', null=True, blank=True)
    apply_end = models.DateField(verbose_name='活动报名结束日期', null=True, blank=True)
    status_choices = (('报名未开始', "报名未开始"), ('报名中', "报名中"), ('报名结束', "报名结束"), ('活动已结束', "活动已结束"))
    status = models.CharField(verbose_name='活动状态', choices=status_choices, max_length=32, default='报名未开始')

    def __str__(self):
        return self.title


class ApplyInfo(models.Model):
    """"""
    apply_id = models.AutoField(verbose_name='活动报名id编号', primary_key=True)
    activity = models.ForeignKey(verbose_name='活动id编号', to='PartyActivity', on_delete=models.CASCADE)
    member = models.ForeignKey(verbose_name='党员id编号', to='Member', on_delete=models.CASCADE)

    class Meta:
        # 联合唯一索引
        unique_together = ('activity', 'member')


class RewardAndPunish(models.Model):
    """奖惩信息表"""

    reward_1 = models.TextField(verbose_name="奖励1级详细内容", max_length=256)
    reward_2 = models.TextField(verbose_name="奖励2级详细内容", max_length=256)
    reward_3 = models.TextField(verbose_name="奖励3级详细内容", max_length=256)

    punish_1 = models.TextField(verbose_name="惩罚1级详细内容", max_length=256)
    punish_2 = models.TextField(verbose_name="惩罚2级详细内容", max_length=256)
    punish_3 = models.TextField(verbose_name="惩罚3级详细内容", max_length=256)


class RewardPunishInfo(models.Model):
    """奖惩详情表"""

    user_account = models.OneToOneField(verbose_name='奖惩对应账号信息外键', to=Member, on_delete=models.CASCADE,
                                        default='')
    reward_level_choices = ((0, '无奖励'), (1, '奖励1级'), (2, '奖励2级'), (3, '奖励3级'))
    reward_level = models.IntegerField(verbose_name='奖励等级', choices=reward_level_choices, default=0)

    punish_level_choices = ((0, '无惩罚'), (1, '惩罚1级'), (2, '惩罚2级'), (3, '惩罚3级'))
    punish_level = models.IntegerField(verbose_name='惩罚等级', choices=punish_level_choices, default=0)


class MeetingRecord(models.Model):
    """会议记录表"""

    date = models.DateField(verbose_name='会议日期')
    place = models.CharField(verbose_name='地点', max_length=32, default='')
    title = models.CharField(verbose_name='会议标题', max_length=128)
    attend_num = models.IntegerField(verbose_name='出勤人数')
    absent_num = models.IntegerField(verbose_name='缺勤人数')
    attendance = models.CharField(verbose_name='出勤名单', max_length=256)
    absence = models.CharField(verbose_name='缺勤名单', max_length=256)


class LectureRecord(models.Model):
    """党课记录表"""

    date = models.DateField(verbose_name='党课日期')
    place = models.CharField(verbose_name='地点', max_length=32)
    title = models.CharField(verbose_name='党课主题', max_length=128)
    attend_num = models.IntegerField(verbose_name='出勤人数')
    absent_num = models.IntegerField(verbose_name='缺勤人数')
    attendance = models.CharField(verbose_name='出勤名单', max_length=256)
    absence = models.CharField(verbose_name='缺勤名单', max_length=256)


class DateSet(models.Model):
    """日期设置"""

    regular_date_set = models.DateField(verbose_name='转正日期设置', null=True, blank=True)
    first_date_set = models.DateField(verbose_name='入党日期设置', null=True, blank=True)
    in_date_set = models.DateField(verbose_name='转入日期设置', null=True, blank=True)
    out_date_set = models.DateField(verbose_name='转出日期设置', null=True, blank=True)


class PartyInfo(models.Model):
    """组织信息表"""

    party_name = models.CharField(verbose_name='组织名称', max_length=64)
    party_secretary = models.CharField(verbose_name='支部书记', max_length=32, null=True, blank=True)
    party_organizer = models.CharField(verbose_name='组织委员', max_length=32, null=True, blank=True)
    party_publicity = models.CharField(verbose_name='宣传委员', max_length=32, null=True, blank=True)
    party_discipline = models.CharField(verbose_name='纪检委员', max_length=32, null=True, blank=True)


class Article(models.Model):
    title = models.CharField('标题', max_length=100)
    content = UEditorField(u'内容', toolbars="full", imagePath="", filePath="",
                           upload_settings={"imageMaxSize": 1204000},
                           settings={}, command=None, blank=True)

    def __str__(self):
        return self.title


class ActivistMeetingRecord(models.Model):
    """积极分子会议记录表"""

    date = models.DateField(verbose_name='会议日期')
    place = models.CharField(verbose_name='地点', max_length=32)
    title = models.CharField(verbose_name='会议标题', max_length=128)
    attend_num = models.IntegerField(verbose_name='出勤人数')
    absent_num = models.IntegerField(verbose_name='缺勤人数')
    attendance = models.CharField(verbose_name='出勤名单', max_length=256)
    absence = models.CharField(verbose_name='缺勤名单', max_length=256)


class ActivistLectureRecord(models.Model):
    """积极分子党课记录表"""

    date = models.DateField(verbose_name='党课日期')
    place = models.CharField(verbose_name='地点', max_length=32)
    title = models.CharField(verbose_name='党课主题', max_length=128)
    attend_num = models.IntegerField(verbose_name='出勤人数')
    absent_num = models.IntegerField(verbose_name='缺勤人数')
    attendance = models.CharField(verbose_name='出勤名单', max_length=256)
    absence = models.CharField(verbose_name='缺勤名单', max_length=256)
