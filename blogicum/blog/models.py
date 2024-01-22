from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model

from core.models import BlogBaseModel


User = get_user_model()


class Post(BlogBaseModel):
    title = models.CharField(max_length=256,
                             verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts')
    image = models.ImageField('Фото', blank=True, upload_to='posts_images')

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_success_url(self):
        return reverse('blog:profile')

    def __str__(self):
        return self.title


class Category(BlogBaseModel):
    title = models.CharField(max_length=256,
                             verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True,
                            verbose_name='Идентификатор',
                            help_text='Идентификатор страницы для URL; '
                            'разрешены символы латиницы, '
                            'цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BlogBaseModel):
    name = models.CharField(max_length=256,
                            verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Публикация'
                             )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Время создания')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments_authored',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
