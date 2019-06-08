from django.conf.urls import url
from . import views

urlpatterns = [
    #  购物车 carts
    url(r'^carts/$', views.CartsView.as_view(),name='info'),
    # 全选购物车/carts/selection/
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view(), name='carts_select'),
    # # 页面简单购物车 /carts/simple/
    url(r'^carts/simple/$', views.CartsSimpleView.as_view(), name='carts_simple'),
]
