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
                    # 查询SKU信息
                    sku = SKU.objects.get(id=sku_id)
                    # 判断SKU库存
                    sku_count = carts_dict[sku.id].get('count')
                    if sku_count > sku.stock:
                        # 出错就回滚
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                    # 模拟延迟
                    # import time
                    # time.sleep(10)

                    # SKU减少库存，增加销量
                    # sku.stock -= sku_count
                    # sku.sales += sku_count
                    # sku.save()


                    # 乐观锁更新库存和销量
                    new_stock = sku.stock - sku_count
                    new_sales = sku.stock + sku_count
                    result = SKU.objects.filter(id=sku_id, stock=sku.stock).update(stock=new_stock,
                                                                                      sales=new_sales)
                    # 如果下单失败，但是库存足够时，继续下单，直到下单成功或者库存不足为止
                    if result == 0:
                        continue
                    # 修改SPU销量
                    sku.spu.sales += sku_count
                    sku.spu.save()

                    # 保存订单商品信息 OrderGoods（多）
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )

                    # 保存商品订单中总价和总数量
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)

                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_id)

            # 清除购物车中已结算的商品
            pl = redis_conn.pipeline()
            pl.hdel(user.id, *carts_dict)
            pl.execute()

            # 响应提交订单结果
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
