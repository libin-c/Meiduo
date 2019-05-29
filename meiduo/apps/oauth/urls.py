from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [

    # QQ 登录
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qq_login'),
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view(),name='oauth_callback'),


]
