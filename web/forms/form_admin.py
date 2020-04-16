#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 19:52


from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django import forms
from DjangoUeditor.forms import UEditorField


class InfoForm(Form):
    """完善信息Form"""
    """修改信息Form"""

    admin_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空', 'invalid': '姓名格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入真实姓名(2-6个字)"})
    )

    admin_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    admin_email = fields.EmailField(
        max_length=32,
        error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
    )

    admin_phone = fields.RegexField(
        regex=r"^1[356789]\d{9}$",
        max_length=32,
        error_messages={'required': '手机号码不能为空', 'invalid': '手机号码格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入手机号码"})
    )


class RewardPunishInfoForm(Form):
    """奖惩Form"""

    reward_1 = fields.CharField(
        label='奖励1级：',
        max_length=256,
        error_messages={'required': '奖励1级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入奖励1级详细内容"})
    )

    reward_2 = fields.CharField(
        max_length=256,
        error_messages={'required': '奖励2级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入奖励2级详细内容"})
    )

    reward_3 = fields.CharField(
        max_length=256,
        error_messages={'required': '奖励3级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入奖励3级详细内容"})
    )

    punish_1 = fields.CharField(
        max_length=256,
        error_messages={'required': '惩罚1级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入惩罚1级详细内容"})
    )

    punish_2 = fields.CharField(
        max_length=256,
        error_messages={'required': '惩罚2级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入惩罚2级详细内容"})
    )

    punish_3 = fields.CharField(
        max_length=256,
        error_messages={'required': '惩罚3级详细内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入惩罚3级详细内容"})
    )


class TransferInForm(Form):
    """党员转入Form"""

    username = fields.CharField(
        min_length=6,
        max_length=13,
        error_messages={'required': '用户名不能为空', 'invalid': '用户名格式有误,请重新输入'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入用户名(6-13位)"})
    )

    member_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空', 'invalid': '姓名格式有误,请重新输入'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入姓名(2-6个汉字)"})
    )

    member_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    member_status = fields.ChoiceField(
        choices=(('正式党员', '正式党员'), ('预备党员', '预备党员')),
        initial='正式党员',
        widget=widgets.Select()
    )

    in_date = forms.DateField(
        error_messages={'required': '转入日期不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    come_from_party = fields.CharField(
        max_length=256,
        error_messages={'required': '转自组织内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入转自什么组织"})
    )


class PartyInfoForm(Form):
    """组织信息Form"""

    party_name = fields.CharField(
        max_length=64,
        error_messages={'required': '组织名称内容不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入组织名称"})
    )

    party_secretary = fields.ChoiceField(
        initial='请选择',
        widget=widgets.Select()
    )

    party_organizer = fields.ChoiceField(
        initial='请选择',
        widget=widgets.Select()
    )

    party_publicity = fields.ChoiceField(
        initial='请选择',
        widget=widgets.Select()
    )

    party_discipline = fields.ChoiceField(
        initial='请选择',
        widget=widgets.Select()
    )


class MemberInfoForm(Form):
    """党员信息修改Form"""

    member_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空!', 'invalid': '姓名格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入姓名(2-6个汉字)"})
    )

    member_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    member_phone = fields.RegexField(
        regex=r"^1[356789]\d{9}$",
        max_length=32,
        error_messages={'required': '手机号码不能为空!', 'invalid': '手机号码格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入手机号码"})
    )

    member_email = fields.EmailField(
        max_length=32,
        error_messages={'required': '邮箱不能为空!', 'invalid': '邮箱格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
    )

    member_status = fields.ChoiceField(
        choices=(('正式党员', '正式党员'), ('预备党员', '预备党员')),
        initial='正式党员',
        widget=widgets.Select()
    )

    first_date = forms.DateField(
        error_messages={'required': '入党日期不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    regular_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    voluntary_time = fields.IntegerField(
        error_messages={'required': '志愿时长不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入正整数的时长"})
    )

    come_from_party = fields.CharField(
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入转自什么组织"})
    )


class ActivistInfoForm(Form):
    """积极分子信息修改Form"""

    activist_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空!', 'invalid': '姓名格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入姓名(2-6个汉字)"})
    )

    activist_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    activist_phone = fields.RegexField(
        regex=r"^1[356789]\d{9}$",
        max_length=32,
        error_messages={'required': '手机号码不能为空!', 'invalid': '手机号码格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入手机号码"})
    )

    activist_email = fields.EmailField(
        max_length=32,
        error_messages={'required': '邮箱不能为空!', 'invalid': '邮箱格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
    )

    apply_date = forms.DateField(
        error_messages={'required': '申请入党日期不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    voluntary_time = fields.IntegerField(
        error_messages={'required': '志愿时长不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入正整数的时长"})
    )


class AddMemberForm(Form):
    """添加成员Form"""

    username = fields.CharField(
        min_length=6,
        max_length=13,
        error_messages={'required': '用户名不能为空!', 'invalid': '用户名格式有误!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入用户名(6-13位)"})
    )

    add_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空!', 'invalid': '姓名格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入姓名(2-6个汉字)"})
    )

    add_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    add_status = fields.ChoiceField(
        choices=(('正式党员', '正式党员'), ('预备党员', '预备党员'), ('积极分子', '积极分子')),
        initial='正式党员',
        widget=widgets.Select()
    )


class ContentForm(Form):
    title = fields.CharField(max_length=100)
    content = UEditorField(u'内容	', height=300, toolbars="full")


class ActivityForm(Form):
    """党日活动Form"""

    title = fields.CharField(
        required=False,
        label='活动主题',
        max_length=128,
        error_messages={'required': '活动主题不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入活动主题"})
    )

    time = fields.DateField(
        required=False,
        label='活动时间',
        error_messages={'required': '活动日期不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    place = fields.CharField(
        required=False,
        label='活动地点',
        max_length=64,
        error_messages={'required': '活动地点不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入活动地点"})
    )
    content = UEditorField(
        u'活动内容',
        required=False,
        height=450,
        toolbars="full",
        error_messages={'required': '活动内容不能为空'},
    )

