from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http.response import HttpResponse, HttpResponseForbidden,JsonResponse
import re

# Create your views here.
# 1. 注册页面 功能
from apps.users.models import User
from meiduo.settings.dev import logger
from utils.response_code import RETCODE


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
        if not re.match(r'^1[345789]\d{9}$', mobile):
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

        # 5.1 成功 重定向到首页re
        return redirect(reverse('contents:index'))
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
