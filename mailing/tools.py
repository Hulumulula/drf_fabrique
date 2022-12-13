import logging

from itertools import chain
from datetime import datetime, timedelta

from django.db.models import Q

from FabricaResheniy.celery import app
from .models import *
from .tasks import send_message

'''Здесь расположены вспомогательные функции-посредники'''

logger = logging.getLogger(__name__)


# Подготовка и сбор данных перед отправкой клиенту
def data_for_send(mailing):
    clients = Client.objects.filter(
        Q(tag=mailing.filter_tag) | Q(code_operator=mailing.filter_codeOperator)
    )

    if not Message.objects.filter(mailingID=mailing):
        messages = []

        for client in clients:
            if not Message.objects.filter(clientID=client, mailingID=mailing).exists():
                messages.append(Message(clientID=client, mailingID=mailing, status='not sent'))

        Message.objects.bulk_create(messages)
    logger.info(f'Передача данных на отправку клиентам: {list(clients)}')

    for message in Message.objects.filter(mailingID=mailing):
        data = {
            'id': message.pk,
            'text': mailing.message,
            'phone': int(message.clientID.phone),
        }

        send_message.delay(data=data, mailing_id=mailing.pk)


# Проверка; возможно ли перенести время отправки сообщения
def check_time_to_request(mailing):
    delta = 0

    if (datetime.now() + timedelta(minutes=35)) < mailing.end_date:
        delta = 30
    elif (datetime.now() + timedelta(minutes=5)) < mailing.end_date:
        delta = 5
    return delta


# Сбор статистики по рассылке. Вывел в отдельную функцию, так как есть повторные использования...
def fun_mails_statistic(mailing_list):
    mailing_statistic = []

    for mailing in mailing_list:
        message = Message.objects.select_related('mailingID').filter(mailingID=mailing)

        message_info = {
            'id': mailing.pk,
            'count_messages': message.count(),
            'count_status_sent': message.filter(status='sent').count(),
            'list_clients_sent': [oneMessage.clientID.phone for oneMessage in message.filter(status='sent').all()],
            'count_status_not_sent': message.filter(status='not sent').count(),
            'list_clients_not_sent': [oneMessage.clientID.phone for oneMessage in
                                      message.filter(status='not sent').all()],
        }

        mailing_statistic.append(message_info)

    return mailing_statistic


# Так как мы не храним нигде ID наших задач из celery напрямую
# я решил использовать inspector для вывода всех задач, которые
# будут выполнены в будущем. Это нужно для обновления задач, если
# пользователь меняет данные рассылки (например даты)
def get_reserved_tasks(mailing_id):
    list_task_id = []

    try:
        # Используем chain из itertools для получения списка всех ключей по нашей рассылке
        for scheduled in chain.from_iterable(app.control.inspect().scheduled().values()):
            if scheduled["request"]["kwargs"]["mailing_id"] == int(mailing_id):
                list_task_id.append(scheduled["request"]["id"])

        if not list_task_id:
            # Запланированных задач - нет!
            list_task_id = False

    except AttributeError as error:
        logger.info(f'Возможно celery не работает... , error: {error}')

    finally:
        return list_task_id
