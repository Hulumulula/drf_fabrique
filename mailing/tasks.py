import smtplib
import time
import requests
import celery

from FabricaResheniy.celery import app
from FabricaResheniy.settings import *
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery import exceptions
from django.utils import timezone
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from requests import exceptions as reqEX
from .models import Message, Mailing


logger = get_task_logger(__name__)


@app.task(bind=True)
def send_message(self, data, mailing_id):
    from .tools import check_time_to_request

    mailing = Mailing.objects.get(pk=mailing_id)

    if mailing.start_date <= timezone.now() <= mailing.end_date:

        headers = {
            'Authorization': f'Bearer {FABRIQUE_TOKEN}',
            'Content-Type': 'application/json'
        }
        url = f'https://probe.fbrq.cloud/v1/send/{data["id"]}'

        try:
            response = requests.post(url, json=data, headers=headers)
        # Если отправить сообщение клиенту не получилось по каким-то причинам,
        # то задача будет переносить себя на 30\5 минут (если позволяет время рассылки)
        except reqEX.ConnectionError as error:
            logger.error(f'Нет связи с сервером c id: {mailing_id}, error: {error}')
            time.sleep(5)
            delta = check_time_to_request(mailing)
            logger.info(f'Сообщение с id {data["id"]} будет повторно отправлено клиенту {data["phone"]} через {delta} минут')
            raise self.retry(eta=timezone.now() + timezone.timedelta(minutes=check_time_to_request(mailing)), exc=error)

        except reqEX as error:
            logger.error(f'Ошибка запроса c id: {mailing_id}, error: {error}')
            time.sleep(5)
            delta = check_time_to_request(mailing)
            logger.info(f'Сообщение с id {data["id"]} будет повторно отправлено клиенту {data["phone"]} через {delta} минут')
            raise self.retry(eta=timezone.now() + timezone.timedelta(minutes=delta), exc=error)

        if response.status_code == 200:
            Message.objects.filter(pk=data['id']).update(status='sent')
            logger.info(f'Сообщение {data["id"]} доставлено клиенту {data["phone"]}!')

        return response.status_code

    elif mailing.end_date < timezone.now():
        logger.info(f'Сообщение не может быть доставлено! Рассылка уже закончилась!')
        return False

    else:

        try:
            self.retry(eta=mailing.start_date)
            logger.info(f'Рассылка с id {mailing.pk} будет запущена в {mailing.start_date}')

        except celery.exceptions.MaxRetriesExceededError:
            logger.error(f'mailing_id: {mailing.pk}, MaxRetriesExceededError')
            return False


@app.task
def send_email():
    from .tools import fun_mails_statistic
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    logger.info(f'Отправляю статистику на почту...')
    try:
        mailing_list = Mailing.objects.all()
        result = fun_mails_statistic(mailing_list)

        subject = 'Mailing Statistic'
        html_message = render_to_string('mailing/mail_template.html', {'context': result})
        plain_message = strip_tags(html_message)
        from_email = EMAIL_HOST_USER
        to = 'Assasin.klimov@yandex.ru'

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            auth_user=EMAIL_HOST_USER,
            auth_password=EMAIL_HOST_PASSWORD,
            fail_silently=False,
            html_message=html_message,
        )
        logger.info('Статистика успешно отправлена на почту!')
        return True
    except smtplib.SMTPException as error:
        logger.error(f'Ошибка отправки статистики на почту, error: {error}')
        return False
    except ObjectDoesNotExist as error:
        logger.error(f'При отправке почты не удалось получить статистику, error: {error}')
        return False


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Отправляет письмо со статистикой каждый день в 12:00
    sender.add_periodic_task(
        crontab(hour=12, minute=0),
        send_email.s(),
    )
