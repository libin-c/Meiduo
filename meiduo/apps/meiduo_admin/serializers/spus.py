from rest_framework import serializers

from apps.contents.models import SPU, Brand, GoodsCategory


class SPUSerializer(serializers.ModelSerializer):
    """
    "counts": "商品SPU总数量",
        "lists": [
            {
                "id": "商品SPU ID",
                "name": "SPU名称",
                "brand": "品牌名称",
                "brand_id": "品牌id",
                "category1_id": "一级分类id",
                "category2_id": "二级分类id",
                "category3_id": "三级分类id",
                "sales": "SPU商品销量",
                "comments": "SPU商品评论量",
                "desc_detail": "商品详情",
                "desc_pack": "商品包装",
                "desc_service": "售后服务"
            },
    """
    # 一级分类id
    category1_id = serializers.IntegerField()
    # 二级分类id
    category2_id = serializers.IntegerField()
    # 三级级分类id
    category3_id = serializers.IntegerField()
    # 关联的品牌id
    brand_id = serializers.IntegerField()
    # 关联的品牌，名称
    brand = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SPU
        exclude = ('category1', 'category2', 'category3')


class SPUBrandsSerizliser(serializers.ModelSerializer):
    """
          SPU表品牌序列化器
    """

    class Meta:
        model = Brand
        fields = '__all__'


class CategorysSerizliser(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'
