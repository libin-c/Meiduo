import base64
import json
import pickle

from django_redis import get_redis_connection

from utils.cookiesecret import CookieSecret


# def merge_cart_cookie_to_redis(request, user, response):
#     """
#     登录后合并cookie购物车数据到Redis
#     :param request: 本次请求对象，获取cookie中的数据
#     :param response: 本次响应对象，清除cookie中的数据
#     :param user: 登录用户信息，获取user_id
#     :return: response
#     """
#     # 获取cookie中的购物车数据
#     cookie_cart_str = request.COOKIES.get('carts')
#     # cookie中没有数据就响应结果
#     if not cookie_cart_str:
#         return response
#     # cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
#     cookie_cart_dict =CookieSecret().loads(cookie_cart_str)
#     new_cart_dict = {}
#     new_cart_selected_add = []
#     new_cart_selected_remove = []
#     # 同步cookie中购物车数据
#     for sku_id, cookie_dict in cookie_cart_dict.items():
#         new_cart_dict[sku_id] = cookie_dict['count']
#
#         if cookie_dict['selected']:
#             new_cart_selected_add.append(sku_id)
#         else:
#             new_cart_selected_remove.append(sku_id)
#
#     # 将new_cart_dict写入到Redis数据库
#     redis_conn = get_redis_connection('carts')
#     pl = redis_conn.pipeline()
#     pl.hmset('carts_%s' % user.id, new_cart_dict)
#     # 将勾选状态同步到Redis数据库
#     if new_cart_selected_add:
#         pl.sadd('selected_%s' % user.id, *new_cart_selected_add)
#     if new_cart_selected_remove:
#         pl.srem('selected_%s' % user.id, *new_cart_selected_remove)
#     pl.execute()
#
#     # 清除cookie
#     response.delete_cookie('carts')
#
#     return response


def merge_cart_cookie_to_redis(request, user, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :param user: 登录用户信息，获取user_id
    :return: response
    """
    # 1.获取cookie数据
    cookie_str = request.COOKIES.get('carts')

    # 2.如果没有数据 就响应结果
    if not cookie_str:
        return response

    # 3.解密
    cookie_dict = CookieSecret.loads(cookie_str)

    # 4.合并购物车数据
    carts_redis_client = get_redis_connection('carts')
    carts_data = carts_redis_client.hgetall(user.id)

    # 将carts_data 二进制字典 转换成 普通字典
    carts_dict = {int(data[0].decode()): json.loads(data[1].decode()) for data in carts_data.items()}

    # 更新数据
    carts_dict.update(cookie_dict)
    # 修改redis的数据
    for sku_id in carts_dict.keys():
        carts_redis_client.hset(user.id, sku_id, json.dumps(carts_dict[sku_id]))

    # 删除cookie值
    response.delete_cookie('carts')

    return response
