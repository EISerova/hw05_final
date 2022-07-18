from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase


class AboutURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.about_url = (
            ('/about/tech/', 'about/tech.html'),
            ('/about/author/', 'about/author.html'),
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        cache.clear()

    def test_about_pages_exist(self):
        """Страницы about доступны пользователям"""
        for url, _ in AboutURLTest.about_url:
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_used_correct_template(self):
        """Проверка вызываемых шаблонов для каждого адреса"""
        for url, template in AboutURLTest.about_url:
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertTemplateUsed(response, template)
