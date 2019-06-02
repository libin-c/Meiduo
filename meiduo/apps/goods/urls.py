from django.conf.urls import url, include
from django.contrib import admin

from apps.goods import views

urlpatterns = [
    url(r'^$', views.GoodsView.as_view(), name='goods'),
    # 注册

]
