from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http.response import HttpResponse, HttpResponseForbidden, JsonResponse
import re

# Create your views here.
# 1. 注册页面 功能
from django_redis import get_redis_connection

from apps.users import constants
from apps.users.models import User
from meiduo.settings.dev import logger
from utils.response_code import RETCODE


class TestView(View):
    def get(self, request):
        return render(request, 'oauth_callback.html')


class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_info.html')


class LogoutView(View):
    def get(self, request):
        """实现退出登录逻辑"""
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = redirect(reverse('users:login'))
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response


class LoginView(View):

    # 登录页面显示
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 1.接收三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验参数
        if not all([username, password]):
            return HttpResponseForbidden('参数不齐全')

            # 2.1 用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 2.2 密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')

        # 3.验证用户名和密码--django自带的认证
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 4.保持登录状态
        login(request, user)
        # 5.是否记住用户名
        if remembered != 'on':
            # 不记住用户名, 浏览器结束会话就过期
            request.session.set_expiry(0)
        else:
            # 记住用户名, 浏览器会话保持两周
            request.session.set_expiry(None)

        # 6.返回响应结果
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
            response.set_cookie('username', username, constants.USERNAME_EXPIRE_TIME)
        return response


class RegisterView(View):

    # 注册页面显示
    def get(self, request):
        return render(request, 'register.html')

    # 注册功能
    def post(self, request):
        # 1. 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 2. 校验 判空 正则
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden('参数不齐')

        # 2.1 校验用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 2.2 校验密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个字符的密码')
        # 2.3 校验两个密码是否一致

        # 2.4 校验手机号
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        # 2.5 是否勾选同意 按钮
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')
        # 3. 注册用户到数据库
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            logger.error(e)
            return render(request, 'register.html', {'register_errmsg': ' 注册失败'})
        # 4. 登录状态
        login(request, user)
        # 5. 返回相应对象
        print(request.POST)
        # 6 验证短信验证吗  msg_code 表单注册

        sms_code = request.POST.get('msg_code')
        # 6.1 从redis 中取出来
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get('sms_%s' % mobile)
        # 6.2.1 判断是否存在
        if redis_code is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # 6.2.2 判断是否相等
        if sms_code != redis_code.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 5.1 成功 重定向到首页re
        response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, constants.USERNAME_EXPIRE_TIME)

        return response


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
