from celery_tasks.main import celery_app


@celery_app.task
def ccp_send_sms_code(mobile, sms_code):
    from libs.yuntongxun.sms import CCP
    send_result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print("当前验证码是:", sms_code)
    return send_result
