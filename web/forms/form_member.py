#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 19:54

from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django import forms

class InfoForm(Form):
    """完善信息Form"""
    # """修改信息Form"""

    member_email = fields.EmailField(
        max_length=32,
        error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
    )

    member_phone = fields.RegexField(
        regex=r"^1[356789]\d{9}$",
        max_length=32,
        error_messages={'required': '手机号码不能为空', 'invalid': '手机号码格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入手机号码"})
    )
    first_date = forms.DateField(
        error_messages={'required': '入党日期不能为空'},
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


class EditInfoForm(Form):
    """修改信息Form"""

    member_name = fields.RegexField(
        regex=r'^[\u4E00-\u9FA5]{2,6}$',
        max_length=32,
        error_messages={'required': '姓名不能为空', 'invalid': '姓名格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入真实姓名(2-6个字)"})
    )

    member_gender = fields.ChoiceField(
        choices=(('男', '男'), ('女', '女')),
        initial='男',
        widget=widgets.Select()
    )

    member_email = fields.EmailField(
        max_length=32,
        error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
    )

    member_phone = fields.RegexField(
        regex=r"^1[356789]\d{9}$",
        max_length=32,
        error_messages={'required': '手机号码不能为空', 'invalid': '手机号码格式有误!'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入手机号码"})
    )
    first_date = forms.DateField(
        error_messages={'required': '入党日期不能为空'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )


    voluntary_time = fields.IntegerField(
        error_messages={'required': '志愿时长不能为空!'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入正整数的时长"})
    )