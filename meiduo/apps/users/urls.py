from django.conf.urls import url
from . import views

urlpatterns = [
    #     url(r'^admin/', admin.site.urls),
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 用户名重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view(),name='count'),
    # 手机号重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view(),name='mobiles'),
    # 登录
    url(r'^login/$', views.LoginView.as_view(),name='login'),
    # 退出登录
    url(r'^logout/$', views.LogoutView.as_view(),name='logout'),
]
