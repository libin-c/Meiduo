from datetime import date, timedelta
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.goods.models import GoodsVisitCount
from apps.meiduo_admin.serializers.goods import GoodsSerializer
from apps.users.models import User


class UserCountView(APIView):
    """
    用户统计
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取用户数量
        :param request:
        :return:
        """

        count = User.objects.filter(is_staff=False).count()
        # 返回结果
        return Response({'count': count})


class UserDayCountView(APIView):
    """
    用户统计
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取当天用户数量
        :param request:
        :return:
        """
        # 获取当天日期
        # now = timezone.now()
        now = date.today()
        count = User.objects.filter(is_staff=False, date_joined__gte=now).count()
        # 返回结果
        return Response({'count': count})


class UserDayActiveCountView(APIView):
    """
     日活跃用户
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        日活跃用户
        :param request:
        :return:
        """
        # 获取当天日期
        # now = timezone.now()
        now = date.today()
        count = User.objects.filter(is_staff=False, last_login__gte=now).count()
        # 返回结果
        return Response({'count': count})


class UserDayOrderCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        日下单用户
        :param request:
        :return:
        """

        now = date.today()
        # 获取当日下单用户数量  orders__create_time 订单创建时间
        user = User.objects.filter(is_staff=False, orderinfo__create_time__gte=now)
        user = set(user)
        count = len(user)
        return Response({
            "count": count,
            "date": now

        })


class UserMonthCountView(APIView):
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取一个月前日期
        start_date = now_date - timedelta(29)
        # 创建空列表保存每天的用户量
        date_list = []

        for i in range(30):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天日期
            cur_date = start_date + timedelta(days=i + 1)
            # 查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
            count = User.objects.filter(is_staff=False, date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)


class GoodsDayView(APIView):

    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取当天访问的商品分类数量信息
        goods = GoodsVisitCount.objects.filter(date=now_date)
        # date_list = []
        # for good in goods:
        #     count = good.count
        #     category = good.category.name
        #     date_list.append({'count': count, 'category': category})
        # return Response(date_list)

        # 序列化返回分类数量
        ser = GoodsSerializer(goods, many=True)
        return Response(ser.data)

