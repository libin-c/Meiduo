from django.db import models
# 1. 导包
from django.contrib.auth.models import AbstractUser


# 2. 继承
class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

# Create your models here.
# 定义用户模型类
# 手动校验用户名密码问题
# 密码加密
# class User(models.Model):
#     username = models.CharField(max_length=20)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=11)
