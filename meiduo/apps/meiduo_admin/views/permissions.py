from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission, ContentType

from apps.meiduo_admin.serializers.permissions import PermissionSerializer, ContentTypeSerializer
from apps.meiduo_admin.utils import PageNum


class PermissionModelViewSet(ModelViewSet):
    """
    规格表的增删改查
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = PermissionSerializer
    # 查询对象
    queryset = Permission.objects.all().order_by('id')
    # 分页器
    pagination_class = PageNum

    # 定义获取权限类型表

    def content_types(self, request):
        # 查询所有权限类型
        content_type = ContentType.objects.all()
        # 返回所有权限类型
        ser = ContentTypeSerializer(content_type, many=True)

        return Response(ser.data)
