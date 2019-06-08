from django.http import HttpResponse, JsonResponse

from apps.verifications import constants
from .constants import *
# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from meiduo.settings.dev import logger
from utils.response_code import RETCODE


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 1. 校验 uuid 正则 已经校验过了

        # 2. 生成图片验证码
        text, image_code = captcha.generate_captcha()

        # 3. 想redis缓存 存验证码

        redis_conn = get_redis_connection('verify_image_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 4. 响应图片验证码
        return HttpResponse(image_code, content_type='imgae/jpeg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, reqeust, mobile):
        """
        :param reqeust: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 2.1 接收图片验证码
        image_code = reqeust.GET.get('image_code')
        uuid = reqeust.GET.get('image_code_id')

        # 2.2 校验图片验证码的正确性
        image_redis_client = get_redis_connection('verify_image_code')
        redis_img_code = image_redis_client.get('img_%s' % uuid)

        # 判断服务器返回的验证
        if redis_img_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效了'})

        # 如果有值 删除redis服务器上的图形验证码
        try:
            image_redis_client.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 2.2 和前端传过来的进行做对比
        # 千万注意: 在redis取出来的是 bytes 类型不能直接做对比 decode()
        if image_code.lower() != redis_img_code.decode().lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        # 2.3 判断有没有send_flag 标识
        # 2.3.1 链接数据库
        sms_redis_client = get_redis_connection('sms_code')
        # 2.3.2 取出标示
        send_flag = sms_redis_client.get('send_flag_%s' % mobile)
        # 2.3.3 如果存在 发送太频繁
        if send_flag:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信太频繁'})
        # 2.3.4 如果不存 吧send_flag 标识一下
        # 3.生成短信验证码,redis-存储
        from random import randint
        sms_code = "%06d" % randint(MIN, MAX)
        try:
            pl = sms_redis_client.pipeline()
            pl.setex('send_flag_%s' % mobile, SMS_SEND_FREQUENT, PO)
            pl.setex("sms_%s" % mobile, SMS_EXPIRATION_TIME, sms_code)
            pl.execute()
        except Exception as e:
            logger.error(e)
        # 4.让第三方 容联云-给手机号-发送短信
        # from libs.yuntongxun.sms import CCP
        #                        手机号           验证码  过期时间5分钟 ,类型默认1
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # print("当前验证码是:", sms_code)
        from celery_tasks.sms.tasks import ccp_send_sms_code
        ccp_send_sms_code.delay(mobile, sms_code)
        # print(sms_code)

        # 5.告诉前端短信发送完毕
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


