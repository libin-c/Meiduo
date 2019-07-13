from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical, users, images, specs, skus, orders, permissions, groups, admin_user, spus, options, \
    channels,brands
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # 登录路由
    url(r'^authorizations/$', obtain_jwt_token),
    # -----------------数据统计--------------------
    url(r'^statistical/total_count/$', statistical.UserCountView.as_view()),
    # 日增加用户statistical/day_increment
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    #  日活跃用户 day_active
    url(r'^statistical/day_active/$', statistical.UserDayActiveCountView.as_view()),
    # 日下单用户 day_orders
    url(r'^statistical/day_orders/$', statistical.UserDayOrderCountView.as_view()),
    #  月注册用户   month_increment
    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    # 日分类商品 goods_day_views
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayView.as_view()),

    # -----------------用户管理--------------------
    url(r'^users/$', users.UserView.as_view()),
    # 商品spu的路由
    url(r'^goods/simple/$', specs.SpecsModelViewSet.as_view({'get': 'simple'})),
    # 商品sku的路由
    url(r'^skus/simple/$', images.ImageModelViewSet.as_view({'get': 'simple'})),
    #  sku 规格路由
    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SKUModelViewSet.as_view({'get': 'specs'})),
    # 权限类型
    url(r'^permission/content_types/$', permissions.PermissionModelViewSet.as_view({'get': 'content_types'})),
    # 用户组获取所有权限
    url(r'^permission/simple/$', groups.GroupModelViewSet.as_view({'get': 'simple'})),
    # 获取用户分组
    url(r'^permission/groups/simple/$', admin_user.AdminModelViewSet.as_view({'get': 'simple'})),

    # 获取品牌分组
    url(r'^goods/brands/simple/$', spus.SPUModelViewSet.as_view({'get': 'brand'})),
    # 获取一级分类 goods/channel/categories
    url(r'^goods/channel/categories/$', spus.SPUModelViewSet.as_view({'get': 'channel'})),
    # 获取二级三级分类 goods/channel/categories
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spus.SPUModelViewSet.as_view({'get': 'channels'})),
    # 规格
    url(r'^goods/specs/simple/$', options.OptionSimple.as_view()),

    url(r'^goods/channel_types/$', channels.GoodsChannelModelViewSet.as_view({'get': 'channel_types'})),
    url(r'^goods/categories/$', channels.GoodsChannelModelViewSet.as_view({'get': 'categories'})),

]

# -----------------商品spu视图--------------------
router = DefaultRouter()
router.register('goods/specs', specs.SpecsModelViewSet, base_name='spec')
urlpatterns += router.urls

# -----------------商品图片视图--------------------
router = DefaultRouter()
router.register('skus/images', images.ImageModelViewSet, base_name='image')
urlpatterns += router.urls

# -----------------商品图SKU视图--------------------
router = DefaultRouter()
router.register('skus', skus.SKUModelViewSet, base_name='skus')
urlpatterns += router.urls

# -----------------订单管理视图--------------------
router = DefaultRouter()
router.register('orders', orders.OrderModeliViewSet, base_name='orders')
urlpatterns += router.urls

# -----------------管理员权限视图--------------------
router = DefaultRouter()
router.register('permission/perms', permissions.PermissionModelViewSet, base_name='permissions')
urlpatterns += router.urls

# -----------------分组表视图--------------------
router = DefaultRouter()
router.register('permission/groups', groups.GroupModelViewSet, base_name='groups')
urlpatterns += router.urls

# -----------------管理员用户视图--------------------
router = DefaultRouter()
router.register('permission/admins', admin_user.AdminModelViewSet, base_name='admin_user')
urlpatterns += router.urls

# ----------------品牌管理视图--------------------
router = DefaultRouter()
router.register('goods/brands', brands.BrandModelViewSet, base_name='brands')
urlpatterns += router.urls

# ----------------频道视图--------------------
rotue = DefaultRouter()
rotue.register('goods/channels', channels.GoodsChannelModelViewSet, base_name='channels')
urlpatterns += rotue.urls

# ----------------SPU视图--------------------
router = DefaultRouter()
router.register('goods', spus.SPUModelViewSet, base_name='spus')
urlpatterns += router.urls

# ----------------规格选项视图--------------------
router = DefaultRouter()
router.register('specs/options', options.OptionModelViewSet, base_name='options')
urlpatterns += router.urls
