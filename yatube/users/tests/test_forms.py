from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_valid_form_create_user(self):
        """Валидная форма создает нового пользователя в базе"""
        form_data = {
            'first_name': 'test_first_name',
            'last_name': 'test last_name',
            'username': 'test',
            'email': 'aaa@aaa.aa',
            'password1': '87654321QQQQ',
            'password2': '87654321QQQQ'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        number_of_users: int = 1
        users_count: int = User.objects.count()
        user_id: int = 1
        new_user: QuerySet[User] = User.objects.get(id=user_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(users_count, number_of_users)
        self.assertEqual(new_user.id, user_id)
        self.assertEqual(new_user.first_name, form_data['first_name'])
        self.assertEqual(new_user.last_name, form_data['last_name'])
        self.assertEqual(new_user.username, form_data['username'])
        self.assertEqual(new_user.email, form_data['email'])
