from collections import OrderedDict

from apps.contents.models import GoodsChannel

# 商品三级列表
def get_categories():
    # 定义一个有序字典
    categories = OrderedDict()
    # 根据group_id sequence 排序
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        # goods_channel ----> 外键找 channel_group
        group_id = channel.group_id  # 当前组
        if group_id not in categories:
            # 组成前段需要的数据格式
            categories[group_id] = {'channels': [], 'sub_cats': []}
            # goods_channel------>goods_category 外键
        cat1 = channel.category
        # 构建channels列表
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        }
        )
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories
