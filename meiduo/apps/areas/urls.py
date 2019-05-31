from django.conf.urls import url
from . import views

urlpatterns = [
    #     url(r'^admin/', admin.site.urls),

    # 查询省市区
    url(r'^areas/$', views.AreasView.as_view(), name='area'),
]
