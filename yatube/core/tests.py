from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_404_page(self):
        """Cтраница 404 отдает шаблон 404.html"""
        response = self.client.get("/nonexist-page/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
