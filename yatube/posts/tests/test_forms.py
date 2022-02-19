import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.query import QuerySet
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class PostFormEditTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.other_group = Group.objects.create(
            title='Другая группа',
            slug='other_slug',
        )
        cls.post = Post.objects.create(
            text='тест',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_valid_form_only_author_edit_post(self):
        """Только автор может изменять пост"""
        base_text: str = self.post.text
        base_group: str = self.post.group
        new_post_text: str = 'Не автор редактирует пост'
        form_data = {
            'text': new_post_text,
            'group': self.other_group.pk
        }

        self.authorized_client.force_login(self.user_not_author)
        response = self.authorized_client.post(
            reverse(
                'posts_page:post_edit', kwargs={
                    'post_id': self.post.pk
                }
            ),
            data=form_data,
            follow=True
        )
        changed_post: QuerySet[Post] = Post.objects.get(
            pk=self.post.pk
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(changed_post.group, base_group)
        self.assertEqual(changed_post.text, base_text)
        self.assertEqual(
            changed_post.author,
            self.user_author,
            msg='Пост отредактировал не автор'
        )

    def test_valid_form_edit_post_and_group(self):
        """Валидная форма изменяет текст и группу поста при редактировании"""
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.other_group.pk,
        }

        response = self.authorized_client.post(
            reverse(
                'posts_page:post_edit', kwargs={
                    'post_id': self.post.pk
                }
            ),
            data=form_data,
            follow=True
        )

        changed_post: QuerySet[Post] = Post.objects.get(
            pk=self.post.pk
        )
        changed_group: str = changed_post.group

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            changed_post.text,
            form_data['text'],
            msg='Редактирование поста не сработало'
        )
        self.assertEqual(
            changed_group.pk,
            form_data['group'],
            msg='Выбор группы не сработал'
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormCreateTest(TestCase):
    """Проверяем соответствие поста отправленной форме"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_valid_form_create_post(self):
        """Валидная форма создает одну запись в Post
        с переданными в форме данными"""
        text: str = 'Тестовый текст'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': text,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts_page:post_create'),
            data=form_data,
            follow=True
        )

        number_of_posts: int = 1
        posts_count: int = Post.objects.count()
        post_id: int = 1
        post: QuerySet[Post] = Post.objects.get(pk=post_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(posts_count, number_of_posts)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, text)
        self.assertEqual(post.image, f'posts/{uploaded.name}')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentFormTest(TestCase):
    """Проверяем соответствие комментария отправленной форме"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='тест',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_form_sent_correct_data(self):
        """Комментарий с корректным текстом
        появляется на странице поста"""
        text: str = 'новый комментарий'
        form_data = {
            'text': text,
            'author': self.user,
            'post': self.post,
        }
        comments_before: int = self.post.comments.count()

        response = self.authorized_client.post(
            reverse(
                'posts_page:add_comment', args={self.post.pk}
            ),
            data=form_data,
            follow=True
        )

        comments_after: int = self.post.comments.count()
        added_comment: QuerySet[Comment] = Comment.objects.first()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(comments_before, comments_after)
        self.assertEqual(added_comment.text, text)
        self.assertEqual(added_comment.author, self.user)
        self.assertEqual(added_comment.post.pk, self.post.pk)

    def test_not_auth_user_forbidden_comment(self):
        """Неавторизованные пользователи
        не могу комментировать посты"""
        text: str = 'новый комментарий'
        form_data = {
            'text': text,
            'post': self.post,
        }
        comments_before: int = self.post.comments.count()

        response = self.guest_client.post(
            reverse(
                'posts_page:add_comment', args={self.post.pk}
            ),
            data=form_data,
            follow=True
        )

        comments_after: int = self.post.comments.count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(comments_before, comments_after)
        self.assertFalse(Comment.objects.filter(text=text).exists())
