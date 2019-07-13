from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import SPUSpecification, SPU
from apps.meiduo_admin.serializers.specs import SPUSpecSerializer, SPUSerializer
from apps.meiduo_admin.utils import PageNum


class SpecsModelViewSet(ModelViewSet):
    """
    规格表的增删改查
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = SPUSpecSerializer
    # 查询对象
    queryset = SPUSpecification.objects.all()
    # 分页器
    pagination_class = PageNum

    # 获取spu的商品信息
    # @action(methods=['GET'], detail=False)
    def simple(self, request):
        # 查询所有spu信息
        spus = SPU.objects.all()

        # 　结果返回
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)
