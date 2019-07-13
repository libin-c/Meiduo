from django.conf import settings
from rest_framework import serializers
from celery_tasks.detail_html.tasks import generate_static_sku_detail_html

from apps.contents.models import SKUImage, SKU
from fdfs_client.client import Fdfs_client


class SKUImageSerializer(serializers.ModelSerializer):
    """
    图片表的序列化器
    """
    sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ('id', 'image', 'sku')

    def create(self, validated_data):
        sku_id = self.context['request'].data.get('sku')
        # 获取保存的图片数据
        img_date = validated_data.get('image')
        # 建立fastdfs的链接对象
        print(settings.FASTDFS_CONF)
        client = Fdfs_client(settings.FASTDFS_CONF)
        #  上传数据
        res = client.upload_by_buffer(img_date.read())
        # 判断上传状态
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError("图片上传失败了")
        img_url = res['Remote file_id']
        # 上传成功获取返回的图片路径信息 将图片信息保存到数据库
        #  因为没有sku_id  前段传的是sku 并且上面限制了read_only 所以我们用一种变通的方式
        image = SKUImage.objects.create(image=img_url, sku_id=sku_id)

        # 调用异步任务 中生产详情页的方法
        generate_static_sku_detail_html.delay(image.sku.id)
        #  返回对象
        return image

    def update(self, instance, validated_data):
        """
        更新图片的操作
        :param instance:
        :param validated_data:
        :return:
        """
        img_date = validated_data.get('image')
        # 建立fastdfs的链接对象
        print(settings.FASTDFS_CONF)
        client = Fdfs_client(settings.FASTDFS_CONF)
        #  上传数据
        res = client.upload_by_buffer(img_date.read())
        # 判断上传状态
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError("图片上传失败了")
        img_url = res['Remote file_id']
        # 上传成功获取返回的图片路径信息 将图片信息保存到数据库
        #  因为没有sku_id  前段传的是sku 并且上面限制了read_only 所以我们用一种变通的方式
        instance.image = img_url
        instance.save()
        # 调用异步任务 中生产详情页的方法
        generate_static_sku_detail_html.delay(instance.sku.id)

        return instance


class SKUSerializer(serializers.ModelSerializer):
    """
    SKU 商品的序列化器
    """

    class Meta:
        model = SKU
        fields = ('id', 'name')
