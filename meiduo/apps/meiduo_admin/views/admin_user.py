from django.contrib.auth.models import Group
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.admin_user import AdminSerializer
from apps.meiduo_admin.serializers.groups import GroupSerializer
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User


class AdminModelViewSet(ModelViewSet):
    """
    规格表的增删改查
    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = AdminSerializer
    # 查询对象
    queryset = User.objects.filter(is_staff=True)
    # 分页器
    pagination_class = PageNum

    # 获取所有分组信息

    def simple(self, request):
        content_type = Group.objects.all()
        # 返回所有权限类型
        ser = GroupSerializer(content_type, many=True)

        return Response(ser.data)