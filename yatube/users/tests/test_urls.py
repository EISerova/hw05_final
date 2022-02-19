from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст больше пятнадцати символов',
            author=cls.user,
            group=cls.group,
        )

        cls.auth_url = (
            (
                '/auth/password_change_form/',
                'users/password_change_form.html'
            ),
            ('/auth/password_change_done/', 'users/password_change_done.html'),
            ('/auth/logout/', 'users/logged_out.html'),
        )

        cls.not_auth_url = (
            ('/auth/signup/', 'users/signup.html'),
            ('/auth/login/', 'users/login.html'),
            ('/auth/password_reset/', 'users/password_reset_form.html'),
            ('/auth/password_reset/done/', 'users/password_reset_done.html'),
            (
                '/auth/reset/<uidb64>/<token>/',
                'users/password_reset_confirm.html'
            ),
            ('/auth/reset/done/', 'users/password_reset_complete.html'),
        )
        cls.all_url = cls.auth_url + cls.not_auth_url

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_see_not_auth_page(self):
        """Общедоступные страницы users доступны"""
        for address, _ in UserURLTest.not_auth_url:
            with self.subTest(address=address):
                response = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_client_change_password_pages(self):
        """Cтраницы смены пароля и выхода из аккаунта
        доступны авторизованным пользователям"""
        for address, _ in UserURLTest.auth_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_correct_template(self):
        """Проверка вызываемых шаблонов для адресов"""
        for address, template in UserURLTest.all_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
