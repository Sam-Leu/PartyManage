from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Create your models here.

class Permission(models.Model):
    """
    权限表
    """
    pid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色
    """
    # 自增ID
    rid = models.AutoField(primary_key=True)
    usertype_choices = (('管理员', "管理员"), ('党员用户', "党员用户"), ('积极分子', "积极分子"))
    usertype = models.CharField(verbose_name='角色ID',choices=usertype_choices,max_length=32)
    # title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)

    def __str__(self):
        return self.usertype


class UserProfile(AbstractUser):
    """
    用户表
    """
    # 自增ID
    uid = models.AutoField(primary_key=True)
    # username，password，email已有
    roles = models.ForeignKey(verbose_name='对应的角色', to='Role', blank=True, on_delete=models.CASCADE)
    is_newuser = models.BooleanField(verbose_name='是否新用户',default=True)

    def __str__(self):
        return self.username


