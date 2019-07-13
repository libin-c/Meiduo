from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import Brand
from apps.meiduo_admin.serializers.brands import BrandSerialzier
from apps.meiduo_admin.utils import PageNum


class BrandModelViewSet(ModelViewSet):
    # 权限
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerialzier
    queryset = Brand.objects.all()
    pagination_class = PageNum
