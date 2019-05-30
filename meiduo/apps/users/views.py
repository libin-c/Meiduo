import json
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http.response import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, \
    HttpResponseServerError
import re

# Create your views here.
# 1. 注册页面 功能
from django_redis import get_redis_connection

from apps.users import constants
from apps.users.models import User
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from celery_tasks.email.tasks import send_verify_email
from meiduo.settings.dev import logger
from utils.response_code import RETCODE

# 邮箱验证
class VerifyEmailView(View):
    def get(self,request):
        """实现邮箱验证逻辑"""
        # 接收参数
        token = request.GET.get('token')

        # 校验参数：判断token是否为空和过期，提取user
        if not token:
            return HttpResponseBadRequest('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return HttpResponseForbidden('无效的token')

        # 修改email_active的值为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('激活邮件失败')

        # 返回邮箱验证结果
        return redirect(reverse('users:info'))

# 邮箱
class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        '''
        实现添加邮箱逻辑
        :param request:
        :return:
        '''
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 校验参数 ---->正则
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseForbidden('参数email有误')

        # 给 email 赋值
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        # 4.异步发送邮件

        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 用户中心
class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)


# 登出
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


# 登录页面
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


# 注册页面逻辑
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


# 用户名验重
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


# 手机验重
class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
