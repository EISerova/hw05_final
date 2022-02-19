from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Модель групп."""
    title = models.CharField(
        max_length=200,
        verbose_name="Название группы"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Атрибут группы"
    )
    description = models.TextField(
        verbose_name="Описание группы"
    )

    class Meta:
        verbose_name: str = "группа"
        verbose_name_plural: str = "Группы"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Post(CreatedModel):
    """Модель сообщений."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа, к которой будет относиться пост"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', 'author')
        verbose_name: str = "опубликованный пост"
        verbose_name_plural: str = "Опубликованные посты"

    def __str__(self) -> str:
        return self.text[:15]


class Comment (CreatedModel):
    """Модель сообщений."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Комментируемый пост"
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name: str = "опубликованный комментарий"
        verbose_name_plural: str = "Опубликованные комментарии"

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    """Модель подписки на авторов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор"
    )
