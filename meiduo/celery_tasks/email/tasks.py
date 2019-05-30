from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import celery_app
from meiduo.settings.dev import logger


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    '''
    subject 邮件标题
    message 普通邮件正文，普通字符串
    from_email 发件人
    recipient_list 收件人列表
    html_message 多媒体邮件正文，可以是html字符串
    :param self:
    :return:
    '''
    subject = '美多商城邮箱验证',
    message = '',
    from_email = settings.EMAIL_FROM,
    recipient_list = [to_email],
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    try:

        # send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
        send_mail(subject, message, from_email, recipient_list, html_message=html_message)
    except Exception as e:
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
