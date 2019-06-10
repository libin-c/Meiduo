from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单　	/orders/commit/
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='order_commit'),
    #　订单成功orders/success/
    url(r'^orders/success/$', views.OrdersSuccessView.as_view(), name='order_success'),

]
