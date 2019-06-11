from django.conf.urls import url
from . import views

urlpatterns = [
    # 支付　	payment/(?P<order_id>\d+)/
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view(), name='payment'),
    #　支付成功payment/status/
    url(r'^payment/status/$', views.PaymentStatusView.as_view(), name='payment_status'),

]
