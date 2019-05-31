from django.conf.urls import url
from . import views

urlpatterns = [
    #     url(r'^admin/', admin.site.urls),
    # 1. 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 2. 用户名重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view(), name='count'),
    # 3. 手机号重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view(), name='mobiles'),
    # 4. 登录
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 5. 退出登录
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 6. 用户中心
    url(r'^info/$', views.InfoView.as_view(), name='info'),
    # 7. 邮箱验证/emails/
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    # 8. 邮箱验证 /emails/verification/
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name='verifyemail'),
    # 9. 地址/address/
    url(r'^address/$', views.AddressView.as_view(), name='address'),
    # 10. 新增地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='create_address'),
    # 11. 修改地址 addresses/(?P<address_id>\d+)/
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateAddressView.as_view(), name='update_address'),
    # 12. 设置默认地址addresses/(?P<address_id>\d+)/default/
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='default_address'),
    # 13. 修改地址标题/addresses/(?P<address_id>\d+)/title/
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleView.as_view(), name='update_title'),
    # 14. 修改密码 /password/
    url(r'^password/$', views.UpdatePwdView.as_view(), name='update_pwd'),
]
