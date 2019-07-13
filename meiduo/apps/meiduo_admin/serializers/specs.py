from rest_framework import serializers

from apps.contents.models import SPUSpecification, SPU


class SPUSpecSerializer(serializers.ModelSerializer):
    """
    商品规格表的序列化器
    """
    # 指定spu的名称  通过模型类的外键
    spu = serializers.StringRelatedField(read_only=True)
    # 指定spu的id值  通过表字段
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = ('id', 'name', 'spu', 'spu_id')


class SPUSerializer(serializers.ModelSerializer):
    """
    SPU 商品的序列化器
    """

    class Meta:
        model = SPU
        fields = ('id', 'name')
