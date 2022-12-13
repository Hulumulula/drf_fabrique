from datetime import timedelta
from rest_framework.test import APITestCase
from mailing.models import Client, Mailing, Message
from django.utils import timezone
from mailing.tasks import send_message, send_email


class SendMessageTestCase(APITestCase):

    def test_send_message(self):
        mailing = Mailing.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
            message='testCelery'
        )
        client = Client.objects.create(phone='79997775544')
        message = Message.objects.create(clientID=client, mailingID=mailing, status='not sent')

        data = {
            'id': 1,
            'text': mailing.message,
            'phone': int(client.phone)
        }
        send = send_message(data=data, mailing_id=mailing.pk)
        self.assertEqual(send, 200)
        message.refresh_from_db()
        self.assertEqual(message.status, 'sent')

    def test_mail_send(self):
        self.assertEqual(send_email(), True)


