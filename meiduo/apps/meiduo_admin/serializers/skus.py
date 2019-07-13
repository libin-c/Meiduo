from rest_framework import serializers
from django.db import transaction
from apps.contents.models import SKU, SKUSpecification, GoodsCategory, SPUSpecification, SpecificationOption


class SpecificationOptionSerializer(serializers.ModelSerializer):
    """
    规格选项序列化器
    """

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """
    sku 具体规格表
    """
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ("spec_id", "option_id")


class SKUSerializer(serializers.ModelSerializer):
    """
    商品规格表的序列化器
    """
    # 指定spu的名称  通过模型类的外键
    spu = serializers.StringRelatedField(read_only=True)
    # 指定spu的id值  通过表字段
    spu_id = serializers.IntegerField()

    # 分类
    category = serializers.StringRelatedField(read_only=True)
    # 分类id
    category_id = serializers.IntegerField()
    # 返回sku 具体规格表
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = "__all__"

    # @transaction.atomic()
    def create(self, validated_data):

        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            # 先提取specs 数据
            specs = validated_data['specs']
            # 删除specs 数据
            del validated_data['specs']
            try:
                #  保存sku

                sku = SKU.objects.create(**validated_data)
                # 　保存sku　具体规格
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku, **spec)

            except:
                transaction.rollback(save_point)
                raise serializers.ValidationError('保存数据失败了')
            else:
                #   进行失误提交
                transaction.savepoint_commit(save_point)
                return sku

    def update(self, instance, validated_data):
        # 更新操作
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            # 先提取specs 数据
            specs = validated_data['specs']
            # 删除specs 数据
            del validated_data['specs']
            try:
                #  更新sku

                SKU.objects.filter(id=instance.id).update(**validated_data)
                #  更新sku　具体规格
                for spec in specs:
                    SKUSpecification.objects.filter(sku=instance, spec=spec['spec_id']).update(**spec)

            except:
                transaction.rollback(save_point)
                raise serializers.ValidationError('保存数据失败了')
            else:
                #   进行失误提交
                transaction.savepoint_commit(save_point)
                return instance


class GoodsCategorySerializer(serializers.ModelSerializer):
    """
    sku 具体规格表
    """

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """
    spu 规格表
    """
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    # 关联的规格选项表
    options = SpecificationOptionSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = "__all__"
