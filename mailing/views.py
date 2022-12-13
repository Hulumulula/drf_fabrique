import logging

from celery.result import AsyncResult
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import *
from .tools import data_for_send, fun_mails_statistic, get_reserved_tasks


logger = logging.getLogger(__name__)


class MailingListView(ModelViewSet):

    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            mailing = serializer.save()
            logger.info(f'Рассылка создана с ID: {mailing.pk}')

            # как только наши данные успешно добавились в БД
            # отправляем данные для создания задачи
            data_for_send(mailing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'Ошибка при создании рассылки, {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):

        # получаем список ID наших задач по рассылке и удаляем их
        tasks_ids = get_reserved_tasks(kwargs.get("pk"))

        if tasks_ids:
            for task_id in tasks_ids:
                AsyncResult(task_id).revoke(terminate=True, signal='SIGKILL')

        logger.info(f'Рассылка удалена с ID: {kwargs.get("pk")}')
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = Mailing.objects.get(pk=kwargs.get("pk"))
        serializer = self.serializer_class(data=request.data, instance=instance)

        if serializer.is_valid():
            # получаем список ID наших задач по рассылке и удаляем их
            tasks_ids = get_reserved_tasks(kwargs.get("pk"))

            if tasks_ids:
                for task_id in tasks_ids:
                    AsyncResult(task_id).revoke(terminate=True, signal='SIGKILL')

            mailing = serializer.save()
            logger.info(f'Рассылка успешно обновлена с ID: {kwargs.get("pk")}')

            # задачи старые удалены - нужно создать новые, с нашими новыми данными
            data_for_send(mailing)

            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.error(f'Ошибка при обновлении рассылки, {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        serializer = MailingSerializer(instance=Mailing.objects.get(pk=kwargs.get("pk")), data=request.data, partial=True)

        if serializer.is_valid():
            # получаем список ID наших задач по рассылке и удаляем их
            tasks_ids = get_reserved_tasks(kwargs.get("pk"))

            if tasks_ids:
                for task_id in tasks_ids:
                    AsyncResult(task_id).revoke(terminate=True, signal='SIGKILL')

            logger.info(f'Рассылка успешно обновлена с ID: {kwargs.get("pk")}')
            mailing = serializer.save()

            # задачи старые удалены - нужно создать новые, с нашими новыми данными
            data_for_send(mailing)

            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.error(f'Ошибка при обновлении рассылки, {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def mailing_info(self, request, *args, **kwargs):
        mailing = self.get_object()
        messages = Message.objects.select_related('mailingID')\
            .filter(mailingID=self.get_object())

        data = {
            'start_date': timezone.localtime(mailing.start_date),
            'end_date': timezone.localtime(mailing.end_date),
            'count_sent_messages': messages.count(),
            'count_status_sent': messages.filter(status='sent').count(),
            'count_status_not_sent': messages.filter(status='not sent').count(),
            'filter_tag': mailing.filter_tag,
            'filter_codeOperator': mailing.filter_codeOperator,
            'clients': [f"{message.clientID.phone} {message.status}" for message in mailing.mail.all()],
            'message_text': mailing.message,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def mailing_statistics(self, request, *args, **kwargs):
        mailing_list = self.queryset
        result = fun_mails_statistic(mailing_list)

        return Response({'statistics': result}, status=status.HTTP_200_OK)


class ClientViewSet(ModelViewSet):

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f'Клиент создан с phone: {request.data["phone"]}')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info(f'Клиент удалён с id: {kwargs.get("pk")}')
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f'Клиент обновлён с id: {kwargs.get("pk")}')
        return super(ClientViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        logger.info(f'Клиент обновлён с id: {kwargs.get("pk")}')
        return super(ClientViewSet, self).partial_update(request, *args, **kwargs)


class MessageViewSet(ModelViewSet):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f'Сообщение создано с id: {request.data["pk"]}')
        return super().create(request, *args, **kwargs)
    