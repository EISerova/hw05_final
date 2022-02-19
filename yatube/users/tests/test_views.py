from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

from ..forms import CreationForm

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            text='тест',
            author=cls.user,
            group=cls.group,
        )
        cls.url_signup = {
            'name': 'users:signup',
            'template': 'users/signup.html'
        }
        cls.url_login = {
            'name': 'users:login',
            'template': 'users/login.html'
        }
        cls.url_password_reset_form = {
            'name': 'users:password_reset_form',
            'template': 'users/password_reset_form.html'
        }
        cls.password_reset_done = {
            'name': 'users:password_reset_done',
            'template': 'users/password_reset_done.html'
        }
        cls.password_reset_complete = {
            'name': 'users:password_reset_complete',
            'template': 'users/password_reset_complete.html'
        }
        cls.password_change_form = {
            'name': 'users:password_change_form',
            'template': 'users/password_change_form.html'
        }
        cls.password_change_done = {
            'name': 'users:password_change_done',
            'template': 'users/password_change_done.html'
        }
        cls.logout = {
            'name': 'users:logout',
            'template': 'users/logged_out.html'
        }
        cls.UID = 'uid'
        cls.token = 'token'
        cls.password_reset_confirm = {
            'name': 'users:password_reset_confirm',
            'template': 'users/password_reset_confirm.html'
        }
        cls.url_templates = (
            cls.url_signup,
            cls.url_login,
            cls.url_password_reset_form,
            cls.password_reset_done,
            cls.password_reset_complete,
            cls.password_change_form,
            cls.password_change_done,
            cls.logout
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template_test(self):
        """view-функциии user используют правильные html-шаблоны"""
        for url in UserURLTest.url_templates:
            with self.subTest(reverse_name=url['name']):
                response = self.authorized_client.get(
                    reverse(url['name'])
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, url['template'])

    def test_password_reset_confirm_page_use_correct_template(self):
        """view-функциия password_reset_confirm использует
        правильный html-шаблон"""
        response = self.authorized_client.get(
            reverse(
                self.password_reset_confirm['name'],
                kwargs={'uidb64': self.UID, 'token': self.token}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(
            response, self.password_reset_confirm['template']
        )

    def test_user_create_page_show_correct_form(self):
        """Шаблон signup сформирован с правильными полями."""
        response = self.guest_client.get(reverse(self.url_signup['name']))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form')

                response_form_field = form_field.fields.get(value)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIsInstance(form_field, CreationForm)
                self.assertIsInstance(response_form_field, expected)
