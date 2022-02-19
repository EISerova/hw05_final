from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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

    def test_models_have_correct_names(self):
        """вывод метода __str__ для text модели Post и title модели Group"""
        post = self.post
        group = self.group
        object_name = {
            str(post): post.text[:15],
            str(group): group.title,
        }
        for str_text, expected_object_name in object_name.items():
            with self.subTest(str_text=str_text):
                self.assertEqual(str_text, expected_object_name)

    def test_post_models_verbose_name(self):
        """verbose совпадает в ожидаемым текстом"""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
