from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.meiduo_admin.serializers.orders import OrderInfoSerializer
from apps.meiduo_admin.utils import PageNum
from apps.order.models import OrderInfo


class OrderModeliViewSet(ReadOnlyModelViewSet):
    """
    订单获取多个和获取一个
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = OrderInfoSerializer
    # # 查询对象
    # queryset = OrderInfo.objects.all()
    # 分页器
    pagination_class = PageNum

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword is '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    # 修改订单状态
    @action(methods=['PUT'], detail=True)
    def status(self, request, pk):
        try:
            #  查询订单状态
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error': '无效的订单状态'})
        # 修改订单状态
        status = request.data.get('status')
        if status is None:
            return Response({'error': '缺少状态值'})
        # 返回对象
        order.status = status
        order.save()
        ser = self.get_serializer(order)
        return Response(ser.data)
