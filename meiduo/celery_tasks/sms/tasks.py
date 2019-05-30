from celery_tasks.main import celery_app


@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
def ccp_send_sms_code(self, mobile, sms_code):
    try:
        from libs.yuntongxun.sms import CCP
        send_result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
        print("当前验证码是:", sms_code)
    except Exception as e:
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
    return send_result
