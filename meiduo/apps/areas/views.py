from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from meiduo.settings.dev import logger
from utils.response_code import RETCODE


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        """提供收货地址界面"""

        return render(request, 'user_center_site.html')


class AreasView(View):
    def get(self, request):
        '''
        提供省市区数据
        :param request:
        :return:
        '''
        area_id = request.GET.get('area_id')

        # 1.0 如果area_id 不存在 查询省
        if not area_id:
            try:

                pro_list = Area.objects.filter(parent__isnull=True)
                # 序列化 省级list
                # 1.0 标准写法
                # province_list = []
                # for pro in pro_list:
                #     province_list.append({'id': pro.id, 'name': pro.name})
                # 2.0 列表推导式
                province_list = [{'id': pro.id, 'name': pro.name} for pro in pro_list]


            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 提供市或区数据
            try:
                parent = Area.objects.get(id=area_id)  # 查询市或区的父级
                subs = parent.subs.all()

                # 序列化市或区数据
                # sub_list = []
                # for sub_model in subs:
                #     sub_list.append({'id': sub_model.id, 'name': sub_model.name})
                sub_list = [{'id': sub.id, 'name': sub.name} for sub in subs]

                sub_data = {
                    'id': parent.id,  # 父级pk
                    'name': parent.name,  # 父级name
                    'subs': sub_list  # 父级的子集
                }
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})

                # 响应市或区数据
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
        # else:
        #     try:
        #         subs = Area.objects.filter(parent_id=area_id)
        #         sub_list = [{'id': sub.id, 'name': sub.name} for sub in subs]
        #         sub_data = {
        #                     # 'id': id,  # 父级pk
        #                     # 'name': name,  # 父级name
        #                     'subs': sub_list  # 父级的子集
        #                 }
        #     except Exception as e:
        #         logger.error(e)
        #         return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
        #
        # return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})