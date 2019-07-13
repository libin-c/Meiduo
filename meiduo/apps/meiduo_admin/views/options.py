from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import SpecificationOption, SPUSpecification
from apps.meiduo_admin.serializers.options import OptionSerialzier, OptionSpecificationSerializer
from apps.meiduo_admin.utils import PageNum


class OptionModelViewSet(ModelViewSet):
    """
    SKU 表的增删改查

    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = OptionSerialzier
    # 查询对象
    queryset = SpecificationOption.objects.all()
    # 分页器
    pagination_class = PageNum

    # def simple(self,request):


class OptionSimple(ListAPIView):
    """
        获取规格信息
    """
    serializer_class = OptionSpecificationSerializer
    queryset = SPUSpecification.objects.all()
