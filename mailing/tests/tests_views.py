from datetime import timedelta
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from mailing.models import Client, Mailing, Message
from django.utils import timezone


class ClientViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        users = [Client(phone=f'7999111223{num}') for num in range(1, 6)]
        Client.objects.bulk_create(users)
        self.user = Client.objects.first()

    def test_list(self):
        url = reverse('client-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Client.objects.count())

    def test_detail(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], 1)
        self.assertEqual(response.json()['phone'], '79991112231')

    def test_post(self):
        url = reverse('client-list')
        data = {'phone': '70003734646'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['phone'], '70003734646')
        self.assertEqual(response.json()['code_operator'], '000')

    def test_put(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        data = {
            "id": 1,
            "phone": "79991112231",
            "code_operator": "999",
            "tag": "test",
            "time_zone": "UTC"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        data = {
            "tag": "test_patch"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tag, 'test_patch')

    def test_delete(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MailingViewSetTestCase(APITestCase):
    start_date = str(timezone.localtime()).replace(' ', 'T')
    end_date = str(timezone.localtime() + timedelta(hours=1)).replace(' ', 'T')

    def setUp(self) -> None:
        mailing_lists = [
            Mailing(start_date=self.start_date, end_date=self.end_date, message='test')
            for _ in range(3)
        ]
        Mailing.objects.bulk_create(mailing_lists)
        self.mailing = Mailing.objects.first()

    def test_list(self):
        url = reverse('mailing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Mailing.objects.count())

    def test_detail(self):
        url = reverse('mailing-detail', kwargs={'pk': self.mailing.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.mailing.pk)

    def test_post(self):
        url = reverse('mailing-list')
        data = {
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'message': 'text',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put(self):
        url = reverse('mailing-detail', kwargs={'pk': self.mailing.pk})
        data = {
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'message': 'text',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        url = reverse('mailing-detail', kwargs={'pk': self.mailing.pk})
        data = {
            'start_date': str(self.start_date),
            'filter_tag': 'chery',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.filter_tag, 'chery')

    def test_delete(self):
        url = reverse('mailing-detail', kwargs={'pk': self.mailing.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @staticmethod
    def helper_mailing_info(self):
        clients = [Client(phone=f'7999888776{num}') for num in range(1, 4)]
        Client.objects.bulk_create(clients)
        messages = [
            Message(clientID=client, mailingID=self.mailing, status='not sent') for client in Client.objects.all()
        ]
        Message.objects.bulk_create(messages)

    def test_mailing_info(self):
        self.helper_mailing_info(self)
        url = reverse('mailing-mailing-info', kwargs={'pk': self.mailing.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'count_sent_messages': 3,
                'count_status_sent': 0,
                'count_status_not_sent': 3,
                'filter_tag': None,
                'filter_codeOperator': None,
                'clients': ['79998887761 not sent', '79998887762 not sent', '79998887763 not sent'],
                'message_text': 'test'
            }
        )

    def test_mailing_statistics(self):
        self.helper_mailing_info(self)
        url = reverse('mailing-mailing-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['statistics'][0], {
                'id': 1,
                'count_messages': 3,
                'count_status_sent': 0,
                'list_clients_sent': [],
                'count_status_not_sent': 3,
                'list_clients_not_sent': ['79998887761', '79998887762', '79998887763'],
            }
        )