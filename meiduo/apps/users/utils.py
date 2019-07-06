import re

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import BadData

from apps.users.models import User

# 自定义认证后端类
from meiduo.settings.dev import logger

from utils.secret import SecretOauth


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


def generate_verify_email_url(user):
    '''
    传递user_id , email
    :param user:
    :return:
    '''
    # 1. 发送的数据
    data_dict = {'user_id': user.id, 'email': user.email}

    # 2. 加密数据
    secret_dict = SecretOauth().dumps(data_dict)

    # 3. 返回拼接的url
    verify_url = settings.EMAIL_ACTIVE_URL + '?token=' + secret_dict
    return verify_url


def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    from utils.secret import SecretOauth
    try:
        token_dict = SecretOauth().loads(token)
    except BadData:
        return None

    try:
        user = User.objects.get(id=token_dict['user_id'], email=token_dict['email'])
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user
