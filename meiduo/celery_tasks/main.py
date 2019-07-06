from celery import Celery
# 2.配置celery可能加载到的美多项目的包
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo.settings.dev")
# 3.创建celery实例

celery_app = Celery('celery_tasks')
# 加载配置文件
celery_app.config_from_object('celery_tasks.config')

# 4.自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])
