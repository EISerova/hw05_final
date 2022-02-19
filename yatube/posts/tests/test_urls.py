from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
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
        cls.public_url = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.pk}/', 'posts/post_detail.html'),
        )
        cls.private_url = (
            (f'/posts/{cls.post.pk}/edit/', 'posts/create_post.html'),
            ('/create/', 'posts/create_post.html'),
        )
        cls.all_url = cls.public_url + cls.private_url
        cls.not_exist_url = '/wrong_url/'
        cls.url_post_for_edit = f'/posts/{cls.post.pk}/edit/'

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_see_public_pages(self):
        """Общедоступные страницы доступны неавторизованным пользователям"""
        for address, _ in PostURLTest.public_url:
            with self.subTest(address=address):
                response = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_and_edit_redirect_not_auth_on_login(self):
        """Страницы /create/ и /edit/ перенаправят неавторизованного пользователя
        на страницу логина."""
        login_url = reverse('users:login')

        for address, _ in PostURLTest.private_url:
            with self.subTest(address=address):
                response = self.guest_client.get(address)

                redirect_url = f'{login_url}?next={address}'
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)

    def test_url_exist_post_create_and_edit_page_for_auth(self):
        """Страницы /create/ и /edit/ доступны авторизованным пользователям"""
        for address, _ in PostURLTest.private_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_correct_template(self):
        """Проверка вызываемых шаблонов для адресов"""
        for address, template in PostURLTest.all_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_wrong_url_return_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404"""
        response = self.guest_client.get(PostURLTest.not_exist_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_not_author_from_page_post_edit(self):
        """Страница /posts/id/edit/ перенаправляет авторизованного пользователя,
        но не автора, на страницу поста """
        self.authorized_client.force_login(self.user_not_author)
        response = self.authorized_client.get(self.url_post_for_edit)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
