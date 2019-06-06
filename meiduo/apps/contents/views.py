from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


class IndexView(View):
    def get(self, request):
        '''
        商品三级列表
        :param request:
        :return:
        '''
        # 商品三级列表
        categories = get_categories()

        # 广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 构建返回数据
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)
