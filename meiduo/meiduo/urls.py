"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 注册
    url(r'^', include('apps.users.urls', namespace='users')),

    # 首页
    url(r'^', include('apps.contents.urls', namespace='contents')),
    # 验证码
    url(r'^', include('apps.verifications.urls', namespace='verifications')),
    # QQ 登录
    url(r'^', include('apps.oauth.urls', namespace='oauth')),
    # 三级联动地址
    url(r'^', include('apps.areas.urls', namespace='areas')),
    # 商品
    url(r'^', include('apps.goods.urls', namespace='goods')),
    # 检索引擎 甘草
    url(r'^search/', include('haystack.urls')),
    # 购物车
    url(r'^', include('apps.carts.urls', namespace='carts')),
    # 订单
    url(r'^', include('apps.order.urls', namespace='order')),
    # 支付
    url(r'^', include('apps.payment.urls', namespace='payment')),
    # 美多后台
    url(r'^meiduo_admin/', include('apps.meiduo_admin.urls')),
]
