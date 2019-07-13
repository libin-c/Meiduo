from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.contents.models import SKU, GoodsCategory, SPU, Brand
from apps.meiduo_admin.serializers.spus import SPUSerializer, SPUBrandsSerizliser, CategorysSerizliser
from apps.meiduo_admin.utils import PageNum


class SPUModelViewSet(ModelViewSet):
    """
    SKU 表的增删改查

    """
    # 权限
    permission_classes = [IsAdminUser]
    # 序列化器
    serializer_class = SPUSerializer
    # 查询对象
    queryset = SPU.objects.all()
    # 分页器
    pagination_class = PageNum

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword is '' or keyword is None:
            return SPU.objects.all()
        else:
            return SPU.objects.filter(name__contains=keyword)

    def brand(self, request):
        # 1、查询所有品牌数据
        data = Brand.objects.all()
        # 2、序列化返回品牌数据
        ser = SPUBrandsSerizliser(data, many=True)

        return Response(ser.data)

    def channel(self, request):
        # 1、获取一级分类数据
        data = GoodsCategory.objects.filter(parent=None)
        # 2、序列化返回分类数据
        ser = CategorysSerizliser(data, many=True)
        return Response(ser.data)

    def channels(self, request, pk):
        # 1、获取二级和三级分类数据
        data = GoodsCategory.objects.filter(parent_id=pk)
        # 2、序列化返回分类数据
        ser = CategorysSerizliser(data, many=True)
        return Response({'subs':ser.data})

    @action(methods=['POST'], detail=False)
    def images(self, request):
        """
            保存图片
        :param request:
        :return:
        """
        # 1、获取图片数据
        data = request.FILES.get('image')
        # 验证图片数据
        if data is None:
            return Response(status=500)

        # 2、建立fastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_CONF)

        # 3、上传图片
        res = client.upload_by_buffer(data.read())

        # 4、判断上传状态
        if res['Status'] != 'Upload successed.':
            return Response({'error': '上传失败'}, status=501)

        # 5、获取上传的图片路径
        image_url = res['Remote file_id']

        # 6、结果返回
        return Response(
            {
                'img_url': settings.FDFS_BASE_URL + image_url
            },

            status=201
        )
