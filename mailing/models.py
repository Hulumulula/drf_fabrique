from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class Mailing(models.Model):
    start_date = models.DateTimeField(verbose_name='Дата начала рассылки')
    message = models.TextField(verbose_name='Текст сообщения')
    filter_tag = models.CharField(max_length=100, verbose_name='Фильтр по тегу', blank=True, null=True)
    filter_codeOperator = models.CharField(max_length=100, verbose_name='Фильтр по коду оператора', blank=True, null=True)
    end_date = models.DateTimeField(verbose_name='Дата окончания рассылки')

    def __str__(self):
        return 'Mailing {}'.format(self.pk)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('Дата начала рассылки не может быть позже даты окончания')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Client(models.Model):
    phoneRegex = RegexValidator(regex=r"^7\d{10}$")
    phone = models.CharField(validators=[phoneRegex], max_length=11, unique=True, verbose_name='Номер телефона')
    code_operator = models.CharField(default='900', max_length=3, verbose_name='Код оператора')
    tag = models.CharField(verbose_name='Произвольный тэг', max_length=100, blank=True)
    tz = models.CharField(default='UTC', verbose_name='Часовой пояс', max_length=100, blank=True)

    def __str__(self):
        return 'Client {}'.format(self.phone)

    def save(self, *args, **kwargs):
        self.code_operator = self.phone[1:4]
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    STATUS = [
        ('sent', 'SENT'),
        ('not sent', 'NOT SENT'),
    ]

    create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания сообщения')
    status = models.CharField(choices=STATUS, max_length=8, verbose_name='Статус сообщения')
    mailingID = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='mail')
    clientID = models.ForeignKey(Client, on_delete=models.PROTECT, null=True, related_name='client')

    def __str__(self):
        return 'Message {}'.format(self.pk)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
