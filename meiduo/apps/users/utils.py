import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


# 自定义认证后端类
def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):

    # 重写父类的认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):

        # # 3.1如果是手机号  验证手机号
        # if re.match('^(1[3-9]\d{9}$)', username):
        #     user = User.objects.get(mobile=username)
        # else:
        #     user = User.objects.get(username=username)
        # if user and user.check.password(password):
        #     return user
        user = get_user_by_account(username)
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user
