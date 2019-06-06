from django.conf.urls import url, include
from django.contrib import admin

from apps.goods import views

urlpatterns = [
    # 1.0 列表分页与排序
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    # 2.0 热销商品 /hot/(?P<category_id>\d+)/
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view(), name='hot_goods'),
    # 3.0 商品详情页 /detail/(?P<sku_id>\d+)/
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
]
