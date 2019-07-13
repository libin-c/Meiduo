from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import SKU, GoodsCategory, SPU
from apps.meiduo_admin.serializers.skus import SKUSerializer, GoodsCategorySerializer, SPUSpecificationSerializer
from apps.meiduo_admin.utils import PageNum


class SKUModelViewSet(ModelViewSet):
    """
    SKU 表的增删改查

    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = SKUSerializer
    # 查询对象
    queryset = SKU.objects.all()
    # 分页器
    pagination_class = PageNum

    # 获取sku 表的所有三级分类信息
    @action(methods=['GET'], detail=False)
    def categories(self, request):
        # 查询三级分类表
        category_data = GoodsCategory.objects.filter(subs=None)
        ser = GoodsCategorySerializer(category_data, many=True)
        #  返回三级分类表数据
        return Response(ser.data)

    # 获取商品的相关规格信息

    def specs(self, request, pk):
        # 根据pk值查询spu商品
        spu = SPU.objects.get(id=pk)
        # 根据spu商品对象返回规格信息
        spec_data = spu.specs.all()
        ser = SPUSpecificationSerializer(spec_data, many=True)

        return Response(ser.data)
