from rest_framework import serializers

from .models import *


class MailingSerializer(serializers.ModelSerializer):
    """Рассылка"""
    def validate(self, data):
        if self.partial:
            if self.instance:
                data["start_date"] = data.get("start_date", self.instance.start_date)
                data["message"] = data.get("message", self.instance.message)
                data["end_date"] = data.get("end_date", self.instance.end_date)

        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError('Дата начала рассылки не может быть позже даты окончания')

        return super().validate(data)

    class Meta:
        model = Mailing
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    """Клиент"""
    class Meta:
        model = Client
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    """Сообщение"""
    class Meta:
        model = Message
        fields = '__all__'
