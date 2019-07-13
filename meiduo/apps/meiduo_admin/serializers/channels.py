from rest_framework import serializers

from apps.contents.models import GoodsChannel, GoodsCategory, GoodsChannelGroup


class GoodsChannelSerialzier(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)
    group_id = serializers.IntegerField()

    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel
        fields = "__all__"


class GoodsCategorySerialzier(serializers.ModelSerializer):
    """
        商品分类序列化器
    """

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsChannelGroupSerialzier(serializers.ModelSerializer):
    """
        商品频道组序列化器
    """

    class Meta:
        model = GoodsChannelGroup
        fields = "__all__"
