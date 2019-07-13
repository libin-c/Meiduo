from rest_framework import serializers

from apps.contents.models import SKU
from apps.order.models import OrderInfo, OrderGoods


class SKUSerializer(serializers.ModelSerializer):
    """
    SKU
    """

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """
    订单商品
    """

    sku =SKUSerializer()
    class Meta:
        model = OrderGoods
        fields = ('count','price','sku')


class OrderInfoSerializer(serializers.ModelSerializer):
    """
    订单的使用字段
    """
    user = serializers.StringRelatedField(read_only=True)
    address = serializers.PrimaryKeyRelatedField(read_only=True)
    # 作为附表
    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
