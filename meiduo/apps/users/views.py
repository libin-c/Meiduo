import json
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http.response import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, \
    HttpResponseServerError
import re

# Create your views here.
# 1. 注册页面 功能
from django_redis import get_redis_connection

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.order.models import OrderInfo
from apps.users import constants
from apps.users.models import User, Address
from apps.users.utils import generate_verify_email_url, check_verify_email_token

from meiduo.settings.dev import logger
from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE
from apps.contents.models import SKU


class UserOrderInfoView(LoginRequiredMixin,View):

    def get(self, request, page_num):

        user = request.user
        # 查询当前登录用户的所有订单
        order_qs = OrderInfo.objects.filter(user=user).order_by('-create_time')
        for order_model in order_qs:

            # 给每个订单多定义两个属性, 订单支付方式中文名字, 订单状态中文名字
            order_model.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order_model.pay_method - 1][1]
            order_model.status_name = OrderInfo.ORDER_STATUS_CHOICES[order_model.status - 1][1]
            # 再给订单模型对象定义sku_list属性,用它来包装订单中的所有商品
            order_model.sku_list = []

            # 获取订单中的所有商品
            order_good_qs = order_model.skus.all()
            # 遍历订单中所有商品查询集
            for good_model in order_good_qs:
                sku = good_model.sku  # 获取到订单商品所对应的sku
                sku.count = good_model.count  # 绑定它买了几件
                sku.amount = sku.price * sku.count  # 给sku绑定一个小计总额
                # 把sku添加到订单sku_list列表中
                order_model.sku_list.append(sku)

        # 创建分页器对订单数据进行分页
        # 创建分页对象
        paginator = Paginator(order_qs, 2)
        # 获取指定页的所有数据
        page_orders = paginator.page(page_num)
        # 获取总页数
        total_page = paginator.num_pages

        context = {
            'page_orders': page_orders,  # 当前这一页要显示的所有订单数据
            'page_num': page_num,  # 当前是第几页
            'total_page': total_page  # 总页数
        }
        return render(request, 'user_center_order.html', context)


class FindPwdView(View):
    def get(self, request):
        return render(request, 'find_password.html')


class ChangePwdView(View):
    def post(self, request, user_id):
        data = request.body.decode()
        data_dict = json.loads(data)
        password = data_dict.get('password')
        password2 = data_dict.get('password2')
        access_token = data_dict.get('access_token')
        # 1.非空
        if not all([access_token, password, password2, ]):
            return HttpResponseForbidden('填写数据不完整')
        if password != password2:
            return HttpResponseForbidden('两个密码不一致')

        user_dict = CookieSecret.loads(access_token)
        if user_dict is None:
            return JsonResponse({}, status=400)

        if int(user_id) != user_dict['user_id']:
            return JsonResponse({}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse({}, status=400)

        user.set_password(password)
        user.save()
        return JsonResponse({})





class UserBrowseHistoryView(LoginRequiredMixin, View):
    def post(self, request):
        """保存用户浏览记录"""
        # 1.接收json参数
        sku_id = json.loads(request.body.decode()).get('sku_id')
        print(sku_id)

        # 2.根据sku_id 查询sku
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在!')

        # 3.如果有sku,保存到redis
        history_redis_client = get_redis_connection('history')
        history_key = 'history_%s' % request.user.id

        redis_pipeline = history_redis_client.pipeline()
        # 3.1 去重
        redis_pipeline.lrem(history_key, 0, sku_id)
        # 3.2 存储
        redis_pipeline.lpush(history_key, sku_id)
        # 3.3 截取 5个
        redis_pipeline.ltrim(history_key, 0, 4)
        redis_pipeline.execute()

        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


class UpdatePwdView(View):
    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        '''
        实现修改密码逻辑
        :param request:
        :return:
        '''
        # 接收参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden('缺少必传参数')

        ret = request.user.check_password(old_password)
        if ret == False:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response


class UpdateTitleView(View):
    def put(self, request, address_id):
        '''
        修改标题
        :param request:
        :return:
        '''
        # 接收参数：地址标题
        json_dict = json.loads(request.body)
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


class DefaultAddressView(View):
    def put(self, request, address_id):
        '''
        # 设置默认地址
        :param request:
        :param address_id:
        :return:
        '''
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

            # 响应设置默认地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息 update 修改
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        # save 修改
        # try:
        #     address = Address.objects.get(id=address_id)
        #     address.user = request.user
        #     address.title = receiver
        #     address.receiver = receiver
        #     address.province_id = province_id
        #     address.city_id = city_id
        #     address.district_id = district_id
        #     address.place = place
        #     address.mobile = mobile
        #     address.tel = tel
        #     address.email = email
        #     address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

            # 响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


# 新增地址
class CreateAddressView(LoginRequiredMixin, View):
    def post(self, request):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user,is_deleted=False).count()
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 地址
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


# 邮箱验证
class VerifyEmailView(View):
    def get(self, request):
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
            return JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '添加邮箱失败'})
        # 4.异步发送邮件

        verify_url = generate_verify_email_url(request.user)
        from celery_tasks.email.tasks import send_verify_email
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
        # user = User.objects.get(username=username,password=password)

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
            response = merge_cart_cookie_to_redis(request=request, user=user, response=response)
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
