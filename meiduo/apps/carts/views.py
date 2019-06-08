import base64
import json
import pickle

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection

from apps.carts import constants
from apps.contents.models import SKU
# Create your views here.
from django.views import View

from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE


# class CartsView(View):
#     def get(self, request):
#         """展示购物车"""
#         user = request.user
#         if user.is_authenticated:
#             # 用户已登录，查询redis购物车
#             redis_conn = get_redis_connection('carts')
#             # 获取redis中的购物车数据
#             redis_cart = redis_conn.hgetall('carts_%s' % user.id)
#             # 获取redis中的选中状态
#             cart_selected = redis_conn.smembers('selected_%s' % user.id)
#
#             # 将redis中的数据构造成跟cookie中的格式一致，方便统一查询
#             cart_dict = {}
#             for sku_id, count in redis_cart.items():
#                 cart_dict[int(sku_id)] = {
#                     'count': int(count),
#                     'selected': sku_id in cart_selected
#                 }
#         else:
#             # 用户未登录，查询cookies购物车
#             cart_str = request.COOKIES.get('carts')
#             if cart_str:
#                 # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
#                 cart_dict = CookieSecret.loads(cart_str)
#                 # cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
#             else:
#                 cart_dict = {}
#                 # 构造购物车渲染数据
#         sku_ids = cart_dict.keys()
#         skus = SKU.objects.filter(id__in=sku_ids)
#         cart_skus = []
#         for sku in skus:
#             cart_skus.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'count': cart_dict.get(sku.id).get('count'),
#                 'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
#                 'default_image_url': sku.default_image.url,
#                 'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
#                 'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
#             })
#
#         context = {
#                 'cart_skus': cart_skus,
#             }
#
#             # 渲染购物车页面
#         return render(request, 'cart.html', context)
#
#     def post(self, request):
#         """添加购物车"""
#         # 接收参数
#         json_dict = json.loads(request.body.decode())
#         sku_id = json_dict.get('sku_id')
#         count = json_dict.get('count')
#         selected = json_dict.get('selected', True)
#
#         # 判断参数是否齐全
#         if not all([sku_id, count]):
#             return HttpResponseForbidden('缺少必传参数')
#         # 判断sku_id是否存在
#         try:
#             SKU.objects.get(id=sku_id)
#         except SKU.DoesNotExist:
#             return HttpResponseForbidden('商品不存在')
#         # 判断count是否为数字
#         try:
#             count = int(count)
#         except Exception:
#             return HttpResponseForbidden('参数count有误')
#         # 判断selected是否为bool值
#         if selected:
#             if not isinstance(selected, bool):
#                 return HttpResponseForbidden('参数selected有误')
#
#         # 判断用户是否登录
#         user = request.user
#         if user.is_authenticated:
#             # 用户已登录，操作redis购物车 采用的是 两张表 carts_use_id 和 selected_use_id
#             redis_conn = get_redis_connection('carts')
#             pl = redis_conn.pipeline()
#             # 新增购物车数据
#             pl.hincrby('carts_%s' % user.id, sku_id, count)
#             # 新增选中的状态
#             if selected:
#                 pl.sadd('selected_%s' % user.id, sku_id)
#             # 执行管道
#             pl.execute()
#             # 响应结果
#             return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
#         else:
#             # 用户未登录，操作cookie购物车
#             cart_str = request.COOKIES.get('carts')
#             # 如果用户操作过cookie购物车
#             if cart_str:
#                 # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
#                 cart_dict = CookieSecret.loads(cart_str)
#                 # cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
#             else:  # 用户从没有操作过cookie购物车
#                 cart_dict = {}
#
#             # 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
#             if sku_id in cart_dict:
#                 # 累加求和
#                 origin_count = cart_dict[sku_id]['count']
#                 count += origin_count
#             cart_dict[sku_id] = {
#                 'count': count,
#                 'selected': selected
#             }
#             # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
#             cookie_cart_str = CookieSecret.dumps(cart_dict)
#             # cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
#
#             # 创建响应对象
#             response = JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
#             # 响应结果并将购物车数据写入到cookie
#             response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
#             return response
#
#     def put(self, request):
#         """修改购物车"""
#         # 接收和校验参数
#         # 接收参数
#         json_dict = json.loads(request.body.decode())
#         sku_id = json_dict.get('sku_id')
#         count = json_dict.get('count')
#         selected = json_dict.get('selected', True)
#
#         # 判断参数是否齐全
#         if not all([sku_id, count]):
#             return HttpResponseForbidden('缺少必传参数')
#         # 判断sku_id是否存在
#         try:
#             sku = SKU.objects.get(id=sku_id)
#         except SKU.DoesNotExist:
#             return HttpResponseForbidden('商品sku_id不存在')
#         # 判断count是否为数字
#         try:
#             count = int(count)
#         except Exception:
#             return HttpResponseForbidden('参数count有误')
#         # 判断selected是否为bool值
#         if selected:
#             if not isinstance(selected, bool):
#                 return HttpResponseForbidden('参数selected有误')
#
#         # 判断用户是否登录
#         user = request.user
#         if user.is_authenticated:
#             # 用户已登录，修改redis购物车
#             redis_conn = get_redis_connection('carts')
#             pl = redis_conn.pipeline()
#             # 因为接口设计为幂等的，直接覆盖
#             pl.hset('carts_%s' % user.id, sku_id, count)
#             # 是否选中
#             if selected:
#                 pl.sadd('selected_%s' % user.id, sku_id)
#             else:
#                 pl.srem('selected_%s' % user.id, sku_id)
#             pl.execute()
#
#             # 创建响应对象
#             cart_sku = {
#                 'id': sku_id,
#                 'count': count,
#                 'selected': selected,
#                 'name': sku.name,
#                 'default_image_url': sku.default_image.url,
#                 'price': sku.price,
#                 'amount': sku.price * count,
#             }
#             return JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
#         else:
#             # 用户未登录，修改cookie购物车
#             # 用户未登录，修改cookie购物车
#             cart_str = request.COOKIES.get('carts')
#             if cart_str:
#                 # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
#                 cart_dict = CookieSecret.loads(cart_str)
#                 # cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
#             else:
#                 cart_dict = {}
#             # 因为接口设计为幂等的，直接覆盖
#             cart_dict[sku_id] = {
#                 'count': count,
#                 'selected': selected
#             }
#             # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
#             cookie_cart_str = CookieSecret.dumps(cart_dict)
#             # cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
#
#             # 创建响应对象
#             cart_sku = {
#                 'id': sku_id,
#                 'count': count,
#                 'selected': selected,
#                 'name': sku.name,
#                 'default_image_url': sku.default_image.url,
#                 'price': sku.price,
#                 'amount': sku.price * count,
#             }
#             response = JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
#             # 响应结果并将购物车数据写入到cookie
#             response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
#             return response
#
#     def delete(self, request):
#         """删除购物车"""
#         # 接收参数
#         json_dict = json.loads(request.body.decode())
#         sku_id = json_dict.get('sku_id')
#
#         # 判断sku_id是否存在
#         try:
#             SKU.objects.get(id=sku_id)
#         except SKU.DoesNotExist:
#             return HttpResponseForbidden('商品不存在')
#
#         # 判断用户是否登录
#         user = request.user
#         if user is not None and user.is_authenticated:
#             # 用户未登录，删除redis购物车
#             redis_conn = get_redis_connection('carts')
#             pl = redis_conn.pipeline()
#             # 删除键，就等价于删除了整条记录
#             pl.hdel('carts_%s' % user.id, sku_id)
#             pl.srem('selected_%s' % user.id, sku_id)
#             pl.execute()
#
#             # 删除结束后，没有响应的数据，只需要响应状态码即可
#             return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
#         else:
#             # 用户未登录，删除cookie购物车
#             cart_str = request.COOKIES.get('carts')
#             if cart_str:
#                 # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
#                 cart_dict = CookieSecret.loads(cart_str)
#                 # cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
#             else:
#                 cart_dict = {}
#
#             # 创建响应对象
#             response = JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
#             if sku_id in cart_dict:
#                 del cart_dict[sku_id]
#                 # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
#                 cookie_cart_str = CookieSecret.dumps(cart_dict)
#                 # cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
#                 # 响应结果并将购物车数据写入到cookie
#                 response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
#             return response


# class CartsSelectAllView(View):
#     """全选购物车"""
#
#     def put(self, request):
#         # 接收参数
#         json_dict = json.loads(request.body.decode())
#         selected = json_dict.get('selected', True)
#
#         # 校验参数
#         if selected:
#             if not isinstance(selected, bool):
#                 return HttpResponseForbidden('参数selected有误')
#
#         # 判断用户是否登录
#         user = request.user
#         if user is not None and user.is_authenticated:
#             # 用户已登录，操作redis购物车
#             redis_conn = get_redis_connection('carts')
#             cart = redis_conn.hgetall('carts_%s' % user.id)
#             sku_id_list = cart.keys()
#             if selected:
#                 # 全选
#                 redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
#             else:
#                 # 取消全选
#                 redis_conn.srem('selected_%s' % user.id, *sku_id_list)
#             return JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
#         else:
#             # 用户已登录，操作cookie购物车
#             cart = request.COOKIES.get('carts')
#             response = JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
#             if cart is not None:
#                 # cart = pickle.loads(base64.b64decode(cart.encode()))
#                 cart = CookieSecret.loads(cart)
#                 for sku_id in cart:
#                     cart[sku_id]['selected'] = selected
#                 # cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
#                 cookie_cart =CookieSecret.dumps(cart)
#                 response.set_cookie('carts', cookie_cart, max_age=constants.CARTS_COOKIE_EXPIRES)
#
#             return response
#
#
# class CartsSimpleView(View):
#     """商品页面右上角购物车"""
#
#     def get(self, request):
#         # 判断用户是否登录
#         user = request.user
#         if user.is_authenticated:
#             # 用户已登录，查询Redis购物车
#             redis_conn = get_redis_connection('carts')
#             redis_cart = redis_conn.hgetall('carts_%s' % user.id)
#             cart_selected = redis_conn.smembers('selected_%s' % user.id)
#             # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
#             cart_dict = {}
#             for sku_id, count in redis_cart.items():
#                 cart_dict[int(sku_id)] = {
#                     'count': int(count),
#                     'selected': sku_id in cart_selected
#                 }
#         else:
#             # 用户未登录，查询cookie购物车
#             cart_str = request.COOKIES.get('carts')
#             if cart_str:
#                 # cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
#                 cart_dict =CookieSecret.loads(cart_str)
#             else:
#                 cart_dict = {}
#
#             # 构造简单购物车JSON数据
#         cart_skus = []
#         sku_ids = cart_dict.keys()
#         skus = SKU.objects.filter(id__in=sku_ids)
#         for sku in skus:
#             cart_skus.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'count': cart_dict.get(sku.id).get('count'),
#                 'default_image_url': sku.default_image.url
#             })
#
#         # 响应json列表数据
#         return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})

# def get_request(request):
#     # 1.0 获取前端的数据
#     json_dict = json.loads(request.body.decode())
#     sku_id = json_dict.get('sku_id')
#     count = json_dict.get('count')
#     selected = json_dict.get('selected', True)
#     user = request.user
#     # 1.用户已登录，查询redis购物车
#     carts_redis_client = get_redis_connection('carts')
#     # 用户未登录，操作cookie购物车
#     cart_str = request.COOKIES.get('carts')
#     return {'sku_id': sku_id, 'count': count, 'selected': selected, 'user': user,
#             'carts_redis_client': carts_redis_client, 'cart_str': cart_str}


class CartsView(View):
    '''
    购物车的 增 删 改 查
    '''

    def get(self, request):
        '''
        展示购物车
        :param request:
        :return:
        '''
        user = request.user
        if user.is_authenticated:
            # 1.用户已登录，查询redis购物车
            carts_redis_client = get_redis_connection('carts')

            # 2.获取当前用户的 所有购物车数据
            carts_data = carts_redis_client.hgetall(request.user.id)

            # 3.转换格式-->和cookie一样的字典 方便后面构建数据
            carts_dict = {int(data[0].decode()): json.loads(data[1].decode()) for data in carts_data.items()}
        else:
            # 用户未登录，查询cookies购物车
            cookie_str = request.COOKIES.get('carts')
            if cookie_str:
                carts_dict = CookieSecret.loads(cookie_str)

            else:
                carts_dict = {}
        sku_ids = carts_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus': cart_skus,
        }

        # 渲染购物车页面
        return render(request, 'cart.html', context)

    def post(self, request):
        '''
        """添加购物车"""
        :param request:
        :return:
        '''
        # 1.0 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 2.0 校验 参数
        # 2.1 判断参数是否齐全
        if not all([sku_id, count]):
            return HttpResponseForbidden('缺少必传参数')
        # 2.2 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在')
        # 2.3 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('参数count有误')
        # 2.3 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected有误')

        # 3.0 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 3.1 登录 使用redis存储
            carts_redis_client = get_redis_connection('carts')

            # 3.2 获取以前数据库的数据
            client_data = carts_redis_client.hgetall(user.id)

            if not client_data:
                # 不存在 新建数据
                carts_redis_client.hset(user.id, sku_id, json.dumps({'count': count, 'selected': selected}))

            # 如果商品已经存在就更新数据
            if str(sku_id).encode() in client_data:
                # 根据sku_id 取出商品
                child_dict = json.loads(client_data[str(sku_id).encode()])
                #  个数累加
                child_dict['count'] += count
                # 更新数据
                carts_redis_client.hset(user.id, sku_id, json.dumps(child_dict))

            else:
                # 增加商品数据
                carts_redis_client.hset(user.id, sku_id, json.dumps({'count': count, 'selected': selected}))

            return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            # 4.0 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 4.1 如果用户操作过cookie购物车
            if cart_str:
                # 4.1.1 解密出明文
                cart_dict = CookieSecret.loads(cart_str)
            else:  # 4.1.2 用户从没有操作过cookie购物车
                cart_dict = {}

            # 4.2 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                # 累加求和
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 转成密文
            cookie_cart_str = CookieSecret.dumps(cart_dict)

            # 创建响应对象
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=24 * 30 * 3600)
            return response

    def put(self, request):
        '''
        修改购物车
        :param request:
        :return:
        '''
        # 1.0 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 2.0 校验参数
        # 2.1 校验 参数
        if not all([sku_id, count]):
            return HttpResponseForbidden('缺少关键参数')
        # 2.2 校验sku_id 是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('该商品不存在')
        # 2.3 校验count 是否为int 类型
        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('count 参数不正确')
        # 2.4 校验 selected 是否为 bool
        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('selected 参数不正确')
        # 3.0 判断是否登录
        user = request.user
        cookie_cart_str = ""
        if user.is_authenticated:
            # 3.1 redis 链接数据库
            carts_redis_client = get_redis_connection('carts')
            # 3.2 覆盖redis 的数据
            new_data = {
                'count': count,
                'selected': selected
            }
            carts_redis_client.hset(user.id, sku_id, json.dumps(new_data))

        else:
            # 用户未登录，删除cookie购物车
            # 4.0 获取cookie
            cart_str = request.COOKIES.get('carts')
            # 4.1 如果存在 解密
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = CookieSecret.loads(cart_str)
            # 4.2 不存在 为空字典
            else:
                cart_dict = {}

            # 覆盖以前的数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 转换成 密文数据
            cookie_cart_str = CookieSecret.dumps(cart_dict)

            # 构建前端的数据
        cart_sku = {
            'id': sku_id,
            'count': count,
            'selected': selected,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': sku.price,
            'amount': sku.price * count,
        }
        response = JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        if not user.is_authenticated:
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
        return response

    def delete(self, request):
        '''
        删除 购物车
        :param request:
        :return:
        '''
        # 1.0 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 2.0 校验
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在')
        # 3.0 判断 是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 3.1 用户登录 redis
            # 3.1.1 链接redis
            carts_redis_client = get_redis_connection('carts')
            # 3.1.2 删除 根据用户id 删除商品sku
            carts_redis_client.hdel(user.id, sku_id)
            # 3.1.3 删除结束后，没有响应的数据，只需要响应状态码即可
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            # 3.2 cookie
            # 3.2.1 获取 cookie
            cart_str = request.COOKIES.get('carts')
            # 3.2.2 如果存在解密
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
                # 4.0 创建响应对象
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            # 4.1循环便利
            if sku_id in cart_dict:
                # 4.2 删除数据
                del cart_dict[sku_id]
                # 4.3 将字典转成密文
                cookie_cart_str = CookieSecret.dumps(cart_dict)
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response


class CartsSelectAllView(View):
    '''
    全选购物车
    '''

    def put(self, request):
        '''
        全选购物车
        :param request:
        :return:
        '''
        # 1.0 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        # 2.0 校验参数
        if selected:
            if not isinstance(selected, bool):
                HttpResponseForbidden('selected 参数不正确')

        # 3.0 判断是否登录
        user = request.user
        if user.is_authenticated:
            # 3.1 登录成功 redis
            # 3.1.1 链接redis
            carts_redis_client = get_redis_connection('carts')
            # 3.1.2 获取所有数据
            carts_data = carts_redis_client.hgetall(user.id)
            # 3.1.3 将所有商品改成True
            # 循环遍历
            for carts in carts_data.items():
                sku_id = carts[0].decode()
                carts_dict = json.loads(carts[1].decode())
                if selected:
                    # 全选
                    carts_dict['selected'] = selected
                else:
                    # 取消全选
                    carts_dict['selected'] = selected
                carts_redis_client.hset(user.id, sku_id, json.dumps(carts_dict))

            return JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
        else:
            # 3.2 未登录 cookie
            # 获取carts 的cookie
            carts_str = request.COOKIES.get('carts')

            response = JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            # 3.2.1 如果存在 解密
            if carts_str is not None:
                carts_dict = CookieSecret.loads(carts_str)
                for sku_id in carts_dict:
                    carts_dict[sku_id]['selected'] = selected
                cookie_cart = CookieSecret.dumps(carts_dict)
                response.set_cookie('carts', cookie_cart, max_age=constants.CARTS_COOKIE_EXPIRES)

            return response


class CartsSimpleView(View):
    """商品页面右上角购物车"""

    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            carts_redis_client = get_redis_connection('carts')
            carts_data = carts_redis_client.hgetall(user.id)
            # 转换格式
            cart_dict = {int(data[0].decode()): json.loads(data[1].decode()) for data in carts_data.items()}
        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
                # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        # 响应json列表数据
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})
