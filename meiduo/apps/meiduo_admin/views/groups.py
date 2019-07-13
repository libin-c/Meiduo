from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, Permission

from apps.meiduo_admin.serializers.groups import GroupSerializer
from apps.meiduo_admin.serializers.permissions import PermissionSerializer
from apps.meiduo_admin.utils import PageNum


class GroupModelViewSet(ModelViewSet):
    """
    规格表的增删改查
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = GroupSerializer
    # 查询对象
    queryset = Group.objects.all()
    # 分页器
    pagination_class = PageNum

    # 获取所有分组权限

    def simple(self, request):
        content_type = Permission.objects.all()
        # 返回所有权限类型
        ser = PermissionSerializer(content_type, many=True)

        return Response(ser.data)
