from django.conf.urls import url
from . import views

urlpatterns = [
    #     url(r'^admin/', admin.site.urls),
    #  地址/address/
    url(r'^address/$', views.AddressView.as_view(), name='address'),
    # 查询省市区
    url(r'^areas/$', views.AreasView.as_view(), name='area'),
]
