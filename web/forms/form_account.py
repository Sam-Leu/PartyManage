#!/usr/bin/env python
# Author: one
# Date: 2020/3/17
# Time: 19:51


from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.forms import PasswordInput
from django import forms
from captcha.fields import CaptchaField


class LoginForm(Form):
    """登陆Form"""
    username = fields.CharField(
        max_length=32,
        error_messages={'required': '用户名不能为空'},
        widget=fields.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入用户名"}))

    password = fields.CharField(
        max_length=32,
        error_messages={'required': '密码不能为空'},
        widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入密码"}))

    usertype = fields.ChoiceField(
        choices=(('管理员', '管理员'), ('党员用户', '党员用户'), ('积极分子', '积极分子'),),
        initial='管理员',
        widget=widgets.RadioSelect()
    )

    captcha = CaptchaField(error_messages={'invalid': '验证码输入有误,请重新输入', 'required': '验证码不能为空'})



class PwdForm(Form):
    """修改密码Form"""

    old_password = fields.CharField(
        max_length=64,
        error_messages={'required': '原密码不能为空'},
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入原密码"})

    )

    new_password = fields.RegexField(
        regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$",
        max_length=64,
        error_messages={'required': '新密码不能为空', 'invalid': '新密码格式有误,请重新输入'},
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "6-12位字母与数字组合"})

    )

    repeat_password = fields.RegexField(
        regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$",
        max_length=64,
        error_messages={'required': '确认密码不能为空', 'invalid': '确认密码格式有误,请重新输入'},
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请再次输入新密码"})

    )