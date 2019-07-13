from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers

from apps.contents.models import Brand


class BrandSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

    def create(self, validated_data):

        # 获取保存的图片数据
        img_date = validated_data.get('logo')
        del validated_data['logo']
        # 建立fastdfs的链接对象

        client = Fdfs_client(settings.FASTDFS_CONF)
        #  上传数据
        res = client.upload_by_buffer(img_date.read())
        # 判断上传状态
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError("图片上传失败了")
        img_url = res['Remote file_id']
        # 上传成功获取返回的图片路径信息 将图片信息保存到数据库
        #  因为没有sku_id  前段传的是sku 并且上面限制了read_only 所以我们用一种变通的方式
        image = Brand.objects.create(logo=img_url,**validated_data)

        #  返回对象
        return image

    def update(self, instance, validated_data):
        """
        更新图片的操作
        :param instance:
        :param validated_data:
        :return:
        """
        img_date = validated_data.get('logo')
        del validated_data['logo']
        # 建立fastdfs的链接对象

        client = Fdfs_client(settings.FASTDFS_CONF)
        #  上传数据
        res = client.upload_by_buffer(img_date.read())
        # 判断上传状态
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError("图片上传失败了")
        img_url = res['Remote file_id']
        # 上传成功获取返回的图片路径信息 将图片信息保存到数据库
        #  因为没有sku_id  前段传的是sku 并且上面限制了read_only 所以我们用一种变通的方式
        instance.logo = img_url
        instance.save()
        # 调用异步任务 中生产详情页的方法

        return instance
