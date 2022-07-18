import shutil
import tempfile
from http import HTTPStatus
from xml.etree.ElementTree import Comment

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='тест',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post
        )
        cls.url_index: dict = {
            'name': 'posts_page:index',
            'template': 'posts/index.html',
            'arg': None
        }
        cls.url_post_create: dict = {
            'name': 'posts_page:post_create',
            'template': 'posts/create_post.html',
            'arg': None
        }
        cls.url_group_list: dict = {
            'name': 'posts_page:group_list',
            'template': 'posts/group_list.html',
            'arg': (cls.group.slug,)
        }
        cls.url_profile: dict = {
            'name': 'posts_page:profile',
            'template': 'posts/profile.html',
            'arg': (cls.user.username,)
        }
        cls.url_post_detail: dict = {
            'name': 'posts_page:post_detail',
            'template': 'posts/post_detail.html',
            'arg': (cls.post.id,)
        }
        cls.url_post_edit: dict = {
            'name': 'posts_page:post_edit',
            'template': 'posts/create_post.html',
            'arg': (cls.post.id,)
        }
        cls.url_templates = (
            cls.url_index,
            cls.url_post_create,
            cls.url_group_list,
            cls.url_profile,
            cls.url_post_detail,
            cls.url_post_edit
        )
        cls.url_templates_context_page_obj = (
            cls.url_index,
            cls.url_group_list,
            cls.url_profile,
        )
        cls.url_templates_create_edit = (
            cls.url_post_create,
            cls.url_post_edit
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template_test(self):
        """view-функциии posts используют правильные html-шаблоны"""
        for url in ViewsURLTest.url_templates:
            with self.subTest(reverse_name=url['name']):
                response = self.authorized_client.get(
                    reverse(url['name'], args=url['arg'])
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, url['template'])

    def test_index_group_list_profile_show_correct_context(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом."""
        for url in ViewsURLTest.url_templates_context_page_obj:
            with self.subTest(reverse_name=url['name']):
                response = self.authorized_client.get(
                    reverse(
                        url['name'], args=url['arg'])
                )

                if response.context.get('page_obj') is None:
                    self.fail('В шаблон не передан page_obj')

                test_post: str = response.context.get('page_obj')[0]
                test_author: str = test_post.author
                test_group: str = test_post.group
                test_image = test_post.image

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(test_post, self.post)
                self.assertEqual(test_author, self.post.author)
                self.assertEqual(test_group, self.post.group)
                self.assertEqual(test_image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                self.url_post_detail['name'], kwargs={
                    'post_id': self.post.pk
                }
            )
        )

        test_post: str = response.context.get('target_post')
        test_image = test_post.image
        comments = test_post.comments.all()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_image, self.post.image)
        self.assertEqual(comments[0], self.comment)

    def test_post_create_and_edit_page_get_correct_form(self):
        """Шаблоны post_create и post_edit
        сформированы с правильными полями."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        fields_count: int = len(form_fields)

        for url in ViewsURLTest.url_templates_create_edit:
            with self.subTest(reverse_name=url['name']):
                response = self.authorized_client.get(
                    reverse(
                        url['name'], args=url['arg'])
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)

                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        response_form: forms.ModelForm = response.context.get(
                            'form'
                        )
                        response_form_field = response_form.fields.get(value)
                        response_form_fields_count: int = len(
                            response_form.fields
                        )

                        self.assertIsInstance(response_form_field, expected)
                        self.assertIsInstance(response_form, PostForm)
                        self.assertEqual(
                            fields_count, response_form_fields_count
                        )

    def test_post_create_contains_context_is_edit_false(self):
        """В контекст шаблона post_create передано значение is_edit: false"""

        response = self.authorized_client.get(
            reverse(self.url_post_create['name'])
        )

        status_is_edit: bool = response.context.get('is_edit')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(status_is_edit)

    def test_post_edit_contains_context_is_edit_true(self):
        """В контекст шаблона post_edit передано значение is_edit: true"""

        response = self.authorized_client.get(
            reverse(
                self.url_post_edit['name'],
                args=self.url_post_edit['arg']
            )
        )

        status_is_edit: bool = response.context.get('is_edit')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(status_is_edit)

    def test_post_not_showing_in_wrong_group(self):
        """Пост не отображается в других группах"""
        wrong_group = Group.objects.create(
            title='Неправильная группа',
            slug='wrong_slug',
        )
        test_post = Post.objects.create(
            text='проверка корректности группы',
            author=self.user,
            group=self.group,
        )

        response = self.authorized_client.get(
            reverse(
                self.url_group_list['name'],
                kwargs={'slug': wrong_group.slug}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(test_post, response.context.get('page_obj'))

    def test_new_post_in_correct_group_profile_index(self):
        """Новый пост отображается на главной странице,
        в выбранной группе, в профайле пользователя"""
        test_post = Post.objects.create(
            text='проверка нового поста',
            author=self.user,
            group=self.group,
        )

        for url in ViewsURLTest.url_templates_context_page_obj:
            with self.subTest(reverse_name=url['name']):
                response = self.authorized_client.get(
                    reverse(
                        url['name'], args=url['arg'])
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn(test_post, response.context.get('page_obj'))


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.url_index: dict = {
            'name': 'posts_page:index',
            'template': 'posts/index.html',
            'arg': None
        }
        cls.url_group_list: dict = {
            'name': 'posts_page:group_list',
            'template': 'posts/group_list.html',
            'arg': (cls.group.slug,)
        }
        cls.url_profile: dict = {
            'name': 'posts_page:profile',
            'template': 'posts/profile.html',
            'arg': (cls.user.username,)
        }
        cls.url_templates_context = (
            cls.url_index,
            cls.url_group_list,
            cls.url_profile
        )
        # Создадаем 12 постов в БД для проверки количества постов на странице.
        number_of_posts: int = 12
        created_posts: list = []
        for _ in range(number_of_posts):
            created_posts.append(
                Post(text='тест', author=cls.user, group=cls.group)
            )
        Post.objects.bulk_create(created_posts)

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_paginator_show_correct_number_page(self):
        """Паджинатор показывает 10 постов"""
        paginator_must_show_posts_on_page: int = 10

        response = self.guest_client.get(
            reverse(self.url_index['name'])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in PaginatorTest.url_templates_context:
            with self.subTest(reverse_name=url['name']):
                response = self.guest_client.get(
                    reverse(
                        url['name'], args=url['arg'])
                )

                posts_on_page: int = len(response.context.get('page_obj'))

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(
                    posts_on_page, paginator_must_show_posts_on_page
                )

    def test_second_page_paginator_show_correct_number_page(self):
        """На второй странице паджинатор показывает 2 поста"""
        expected_count: int = 2

        response = self.guest_client.get(
            reverse(self.url_index['name']), {
                'page': expected_count
            }
        )

        posts_on_page: int = len(response.context.get('page_obj'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(posts_on_page, expected_count)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.url_index: dict = {
            'name': 'posts_page:index',
            'template': 'posts/index.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_main_page(self):
        """Кэширование списка постов на главной странице"""
        cache.clear()

        created_post = Post.objects.create(text='тест кэша', author=self.user)
        response = self.guest_client.get(reverse(self.url_index['name']))
        cache_with_post = response.content

        created_post.delete()
        response = self.guest_client.get(reverse(self.url_index['name']))
        cache_delete_post = response.content

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(cache_with_post, cache_delete_post)

        cache.clear()
        response = self.guest_client.get(reverse(self.url_index['name']))
        clear_cache = response.content

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(cache_with_post, clear_cache)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth'
        )
        cls.following_user = User.objects.create_user(
            username='follow_user'
        )
        cls.unfollowing_user = User.objects.create_user(
            username='unfollow_user'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.url_follow: dict = {
            'name': 'posts_page:profile_follow',
            'template': 'posts/follow.html',
            'arg': (cls.user,)
        }
        cls.url_unfollow: dict = {
            'name': 'posts_page:profile_unfollow',
            'template': 'posts/unfollow.html',
            'arg': (cls.user,)
        }
        cls.url_follow_index: dict = {
            'name': 'posts_page:follow_index',
            'template': 'posts/follow.html'
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.following_user)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollowing_user)

    def test_follow_user(self):
        """Авторизованный пользователь может подписываться
        на других пользователей """
        Post.objects.create(text='тест подписки', author=self.user)

        self.follower_client.get(
            reverse(self.url_follow['name'], args=self.url_follow['arg'])
        )

        following_exist = Follow.objects.filter(
            user=self.following_user, author=self.user
        ).exists()

        self.assertTrue(following_exist)

    def test_unfollow_user(self):
        """Авторизованный пользователь может удалять
        подписки на других авторов"""
        Follow.objects.create(user=self.following_user, author=self.user)
        self.follower_client.get(
            reverse(self.url_unfollow['name'], args=self.url_unfollow['arg'])
        )
        following_exist = Follow.objects.filter(
            user=self.following_user, author=self.user
        ).exists()

        self.assertFalse(following_exist)

    def test_update_following_list(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан """
        post = Post.objects.create(text='тест подписки', author=self.user)
        Follow.objects.create(user=self.following_user, author=self.user)

        response = self.follower_client.get(reverse(self.url_follow['name']))

        following_list = response.context.get('page_obj')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(post, following_list)

    def test_update_following_list(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан"""
        post = Post.objects.create(text='тест подписки', author=self.user)

        response = self.unfollower_client.get(
            reverse(self.url_follow_index['name'])
        )

        following_list = response.context.get('page_obj')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(post, following_list)
