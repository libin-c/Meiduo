from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import SKUImage, SKU
from apps.meiduo_admin.serializers.images import SKUImageSerializer, SKUSerializer
from apps.meiduo_admin.utils import PageNum


class ImageModelViewSet(ModelViewSet):
    """
    图片表
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = SKUImageSerializer
    # 查询对象
    queryset = SKUImage.objects.all()
    # 分页器
    pagination_class = PageNum


    # 获取spu的商品信息
    # @action(methods=['GET'],detail=False)
    def simple(self, request):
        # 查询所有spu信息
        spus = SKU.objects.all()

        # 　结果返回
        ser = SKUSerializer(spus, many=True)
        return Response(ser.data)
