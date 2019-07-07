import re

from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseServerError, HttpResponseForbidden,HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.oauth import sinaweibopy3
from apps.oauth.models import OAuthQQUser, OAuthSinaUser
from apps.oauth.utils import Signature
from utils.cookiesecret import CookieSecret
from utils.secret import SecretOauth
from apps.users import constants
from apps.users.models import User
from meiduo.settings.dev import logger
from utils.response_code import RETCODE


def is_bind_openid(openid, request):
    try:
        # openid = SecretOauth().loads(openid).get('openid')
        oauth_user = OAuthQQUser.objects.get(openid=openid)
    except Exception as e:
        logger.error(e)
        context = SecretOauth().dumps(openid)
        context = {'openid': context}

        return render(request, 'oauth_callback.html', context=context)
    else:
        # 如果openid已绑定美多商城用户
        # 实现状态保持
        qq_user = oauth_user.user
        login(request, qq_user)

        # 重定向到主页
        response = redirect(reverse('contents:index'))

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)

        return response


class QQAuthURLView(View):
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthUserView(View):
    """用户扫码登录的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 提取code请求参数
        code = request.GET.get('code')
        if not code:
            return HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI
        )

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
            response = is_bind_openid(openid, request)
            print(openid)
            return response
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('OAuth2.0认证失败')

    def post(self, request):
        """美多商城用户绑定到openid"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')
        print(openid)
        openid = SecretOauth().loads(openid)


        # 判断参数是否齐全
        if not all([mobile, pwd]):
            return HttpResponseForbidden('参数不齐')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致

        sms_code = request.POST.get('msg_code')
        # 6.1 从redis 中取出来
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get('sms_%s' % mobile)

        if redis_code is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code != redis_code.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效：错误提示放在sms_code_errmsg位置


        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 如果用户存在，检查用户密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 将用户绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 实现状态保持
        login(request, user)

        # 响应绑定结果
        next = request.GET.get('state')
        response = redirect(next)
        response = merge_cart_cookie_to_redis(request=request, user=user, response=response)

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response

#

class OAuthSinaURLView(View):
    def get(self, request):
        next_url = request.GET.get('next')

        # 创建授权对象
        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,redirect_uri=settings.REDIRECT_URL)
        # 生成授权地址

        login_url =client.get_authorize_url()

        # 响应
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': "OK",
            'login_url': login_url
        })


class OAuthSinaOpenidView(View):
    def get(self, request):
        code = request.GET.get('code')

        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,redirect_uri=settings.REDIRECT_URL)

        # 1.根据code获取access_token


        result = client.request_access_token(code)
        client.set_access_token(result.access_token, result.expires_in)
        openid=result.uid
        print('openid={}'.format(openid))
        # 判断是否初次授权
        try:
            qquser = OAuthSinaUser.objects.get(uid=openid)
        except:
            # 未查到数据，则为初次授权，显示绑定页面
            # 将openi加密
            json_str = CookieSecret.dumps(openid)
            # 显示绑定页面
            context = {
                'openid': json_str
            }
            return render(request, 'oauth_callback.html', context)

            # 查询到授权对象，则状态保持，转到相关页面
        user = qquser.user
        login(request, user)

        response = redirect(reverse('contents:index'))


        response.set_cookie('username', user.username)
        return response


    def post(self, request):
        # 接收：openid,mobile,password,sms_code
        openid = request.POST.get('openid')
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code = request.POST.get('msg_code')
        state = request.GET.get('state', '/')

        # 验证：参考注册的验证
        # openid_dict = meiduo_signature.loads(access_token, constants.OPENID_EXPIRES)
        if openid is None:
            return HttpResponseForbidden('授权信息无效，请重新授权')
        # openid=openid_dict.get('openid')

        # sms_code = request.POST.get('msg_code')
        # 6.1 从redis 中取出来
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get('sms_%s' % mobile)

        if redis_code is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code != redis_code.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 处理：初次授权，完成openid与user的绑定
        # 1.判断手机号是否已经使用
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 2.如果未使用，则新建用户
            user = User.objects.create_user(mobile, password=pwd, mobile=mobile)
        else:
            # 3.如果已使用，则验证密码
            # 3.1密码正确，则继续执行
            if not user.check_password(pwd):
                # 3.2密码错误，则提示
                return HttpResponseForbidden('手机号已经使用，或密码错误')

        # 4.绑定：新建OAuthSinaUser对象
        qquser = OAuthSinaUser.objects.create(
            user=user,
            uid=openid
        )
        # 状态保持
        login(request, user)
        response = redirect(state)
        response.set_cookie('username', user.username)

        # 响应
        return response


