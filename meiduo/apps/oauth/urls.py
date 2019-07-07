from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [

    # QQ 登录
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qq_login'),
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view(), name='oauth_callback'),
    # 获取新浪登录页面连接
    url('^sina/login/$', views.OAuthSinaURLView.as_view()),
    # 绑定新浪账户
    url('^sina_callback$', views.OAuthSinaOpenidView.as_view()),


]
