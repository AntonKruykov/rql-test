import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class CreateNewUserTest(APITestCase):
    def setUp(self):
        self.valid_payload = {
            'username': 'alice',
            'email': 'alice@test.te',
            'last_name': 'Alison',
            'first_name': 'Alice'
        }
        self.invalid_payload = {
            'username': '',
            'email': 'bob@test.te',
            'last_name': 'Parker',
            'first_name': 'Bob'
        }

    def test_create_valid_user(self):
        response = self.client.post(
            reverse('user-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        response = self.client.post(
            reverse('user-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReadUserTest(APITestCase):
    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='alice',
            defaults={
                'email': 'alice@test.te',
                'last_name': 'Alison',
                'first_name': 'Alice'
            })

    def test_read_user(self):
        response = self.client.get(
            reverse('user-detail', [self.user.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)


class EditUserTest(APITestCase):
    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='alice',
            defaults={
                'email': 'alice@test.te',
                'last_name': 'Alison',
                'first_name': 'Alice'
            })
        self.valid_payload = {
            'username': 'alice_edites',
            'email': 'alice_edites@test.te',
            'last_name': 'Alison_edited',
            'first_name': 'Alice_edited'
        }
        self.invalid_payload = {
            'username': 'alice_edites',
            'email': 'alice_edites.test.te',
            'last_name': 'Alison_edited',
            'first_name': 'Alice_edited'
        }

    def test_edit_valid_user(self):
        response = self.client.put(
            reverse('user-detail', [self.user.id]),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'],
                         self.valid_payload['username'])
        self.assertEqual(response.data['email'], self.valid_payload['email'])

    def test_edit_invalid_user(self):
        response = self.client.put(
            reverse('user-detail', [self.user.id]),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteUsersTest(APITestCase):
    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='alice',
            defaults={
                'email': 'alice@test.te',
                'last_name': 'Alison',
                'first_name': 'Alice'
            })

    def test_delete_user(self):
        self.assertEqual(User.objects.filter(pk=self.user.pk).count(), 1)
        response = self.client.delete(
            reverse('user-detail', [self.user.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(pk=self.user.pk).count(), 0)


class UsersTest(APITestCase):
    def setUp(self):
        User.objects.all().delete()
        for i in range(10):
            User.objects.create(username='name{}'.format(i),
                                email='email{}@test.te'.format(i),
                                first_name='first{}'.format(i),
                                last_name='last{}'.format(i))


class ListUsersTest(UsersTest):
    def test_list_users(self):
        response = self.client.get(
            reverse('user-list',),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)


class LestRQLUsersTest(UsersTest):
    def test_eq(self):
        q = 'username==name5'
        response = self.client.get(
            reverse('user-list', ) + '?q={}'.format(q),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['email'], 'email5@test.te')

    def test_in(self):
        q = 'username=in=(name5,name6,name2)'
        response = self.client.get(
            reverse('user-list', ) + '?q={}'.format(q),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_and(self):
        q = 'username=in=(name5,name6,name2);first_name==first6'
        response = self.client.get(
            reverse('user-list', ) + '?q={}'.format(q),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_or(self):
        q = 'username=in=(name5,name6,name2),' \
            'first_name=in=(first6,first3,first2)'
        response = self.client.get(
            reverse('user-list', ) + '?q={}'.format(q),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_or_and(self):
        q = '(username==name5,username==name6);' \
            '(first_name==first6,first_name==first2)'
        response = self.client.get(
            reverse('user-list', ) + '?q={}'.format(q),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'email6@test.te')
