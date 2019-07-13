from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from apps.meiduo_admin.serializers.users import UserSerializer
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User


class UserView(ListCreateAPIView):
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = UserSerializer
    # 查询对象
    queryset = User.objects.filter(is_staff=False)
    # 分页器
    pagination_class = PageNum

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword is '' or keyword is None:
            return User.objects.filter(is_staff=False)
        else:
            return User.objects.filter(username__contains=keyword, is_staff=False)
