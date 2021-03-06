"""
Django settings for meiduo project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print('开发测试环境',BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-6r@hx*#1niq0+@7hjog)u0s3y*%(-rb2%thk-4t81fe^y43z9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.meiduo.site', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 注册子应用
    'apps.users',
    # 首页子应用
    'apps.contents',
    # 验证码子应用
    'apps.verifications',
    # QQ认证
    'apps.oauth',
    # 地址认证
    'apps.areas',
    # 商品认证
    'apps.goods',
    # 检索引擎 甘草
    'haystack',
    # 购物车应用
    'apps.carts',
    # 订单应用
    'apps.order',
    # 支付应用
    'apps.payment',
    # 美多后台
    'apps.meiduo_admin',

    'django_crontab',  # 定时任务

    'corsheaders',  # cors 同源策略跨域访问的问题

]
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    (
        '*/1 * * * *', 'apps.contents.crons.generate_static_index_html',
        '>> ' + os.path.join(BASE_DIR, 'logs/crontab.log'))
]

CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 跨域资源共享的中间件
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo.urls'
# jinja2 模板
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # 1.jinja2模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 2.模本文件夹路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 3.加载Jinja2模板引擎环境
            'environment': 'utils.jinja2_env.jinja2_environment',
        },
    },
]

WSGI_APPLICATION = 'meiduo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
#         'HOST': '127.0.0.1',  # 数据库主机
#         'PORT': 3306,  # 数据库端口
#         'USER': 'libin',  # 数据库用户名
#         'PASSWORD': 'root',  # 数据库用户密码
#         'NAME': 'meiduo'  # 数据库名字
#     },
# }
DATABASES = {
    'default': {  # 写（主机）
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'HOST': '39.96.172.253',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'libin',  # 数据库用户名
        'PASSWORD': 'root',  # 数据库用户密码
        'NAME': 'meiduo'  # 数据库名字
    },
    'slave': {  # 读（从机）
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '39.96.172.253',
        'PORT': 8306,
        'USER': 'root',
        'PASSWORD': 'root',
        'NAME': 'meiduo'
    }
}
DATABASE_ROUTERS = ['utils.db_router.MasterSlaveDBRouter']
# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# 配置静态文件
STATIC_URL = '/static/'

# 配置静态文件加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# 注释掉 STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# redis 数据库
CACHES = {
    "default": {  # 默认
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_image_code": {  # # 保存图片验证码--2号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sms_code": {  # 保存短信验证码--3号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}
# 实例化日志对象
import logging

logger = logging.getLogger('django')

# 设置自己的users 应用
AUTH_USER_MODEL = 'users.User'

# 指定自定义的用户认证后端
AUTHENTICATION_BACKENDS = ['apps.users.utils.UsernameMobileAuthBackend']

# 设置登录的路由
LOGIN_URL = '/login/'

# QQ设置
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 6.配置邮件服务器

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
# EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
# EMAIL_PORT = 25  # 发邮件端口
# EMAIL_HOST_USER = 'w403600@163.com'  # 授权的邮箱
# EMAIL_HOST_PASSWORD = 'w12530798'  # 邮箱授权时获得的密码，非注册登录密码
# EMAIL_FROM = '美多商城<hmmeiduo@163.com>'  # 发件人抬头
# # 邮箱验证链接
# EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'
# 网易邮箱的配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST_USER = 'w403600@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = 'w12530798'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<hmmeiduo@163.com>'  # 发件人抬头
# 邮箱验证链接
EMAIL_ACTIVE_URL = 'http://www.meiduo.site:8000/emails/verification/'  # 激活地址

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'utils.fastdfs.fdfs.FastDFSStorage'

# FastDFS相关参数
# FDFS_BASE_URL = 'http://192.168.103.158:8888/'
FDFS_BASE_URL = 'http://39.96.172.253:8888/'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://39.96.172.253:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo',  # Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 阿里支付
ALIPAY_APPID = '2016092800618448'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

# 微博登录
APP_KEY = '3305669385'
APP_SECRET = '74c7bea69d5fc64f5c3b80c802325276'
REDIRECT_URL = 'http://www.meiduo.site:8000/sina_callback'

# CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://39.96.172.253:8080',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

REST_FRAMEWORK = {
    # 全局认证设置
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    # 设置有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 设置JWT 返回数据的方法

    'JWT_RESPONSE_PAYLOAD_HANDLER': 'apps.meiduo_admin.utils.jwt_response_payload_handler',
}


FASTDFS_CONF=os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
