from django.db import models

from apps.contents.models import GoodsCategory
# Create your models here.
from utils.models import BaseModel


class GoodsVisitCount(BaseModel):
    """统计分类商品访问量模型类"""
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='商品分类')
    count = models.IntegerField(verbose_name='访问量', default=0)
    date = models.DateField(auto_now_add=True, verbose_name='统计日期')

    class Meta:
        db_table = 'tb_goods_visit'
        verbose_name = '统计分类商品访问量'
        verbose_name_plural = verbose_name