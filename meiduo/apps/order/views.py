import json
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render

# Create your views here.


from django.views import View
from django_redis import get_redis_connection

from apps.contents.models import SKU
from apps.order import constants
from apps.order.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.response_code import RETCODE


class OrderCommitView(LoginRequiredMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存的订单数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseForbidden('参数pay_method错误')

        # 获取登录用户
        user = request.user
        # 生成订单编号：年月日时分秒+用户编号
        # order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            try:
                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=constants.TOTAL_COUNT,
                    total_amount=Decimal(constants.TOTAL_AMOUNT),
                    freight=Decimal(constants.FREIGHT),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_data = redis_conn.hgetall(user.id)
                # cart_dict = {int(data[0].decode()): json.loads(data[1].decode()) for data in carts_data.items()}
                carts_dict = {}
                for carts in redis_data.items():
                    sku_id = int(carts[0].decode())
                    sku_dict = json.loads(carts[1].decode())
                    if sku_dict['selected']:
                        carts_dict[sku_id] = sku_dict

                sku_ids = carts_dict.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)

                        # 原始销量 和  库存量
                        origin_sales = sku.sales
                        origin_stock = sku.stock

                        # 判断库存是否充足
                        sku_count = carts_dict[sku_id]['count']
                        if sku_count > sku.stock:
                            # 事物回滚
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 模拟资源抢夺
                        # import time
                        # time.sleep(10)
                        # sku减少库存, 增加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 使用乐观锁 更新库存量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)

                        # 如果下单下单失败,库存足够则继续下单,直到下单成功或者库存不足
                        if result == 0:
                            continue

                        # SPU 增加销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 保存商品订单中总价和总数量
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)

                        # 下单成功 或失败跳出
                        break

                        # 添加邮费和保存订单
                    order.total_amount += order.freight
                    order.save()

            except Exception as e:
                # 事物回滚
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': RETCODE.OK, 'errmsg': '下单失败'})

                # 提交事物
            transaction.savepoint_commit(save_id)

            # 清除购物车已经结算过的商品
        redis_conn.hdel(user.id, *carts_dict)

            # 返回响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})



# 3.订单成功
class OrdersSuccessView(View):
    def get(self, request):
        # 1.接收参数 GET
        order_id = request.GET.get('order_id')
        pay_method = request.GET.get('pay_method')
        payment_amount = request.GET.get('payment_amount')

        # 2.组合数据
        context = {
            "order_id": order_id,
            "pay_method": pay_method,
            "payment_amount": payment_amount

        }
        return render(request, 'order_success.html', context)
