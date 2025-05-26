from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

t1 = 'Идентификатор страницы для URL; разрешены символы '
t2 = 'латиницы, цифры, дефис и подчёркивание.'
t3 = 'Если установить дату и время в будущем — можно '
t4 = 'делать отложенные публикации.'


class Category(models.Model):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text=t1 + t2
    )
    is_published = models.BooleanField(
        default=True,
        blank=False,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места'
    )
    is_published = models.BooleanField(
        default=True,
        blank=False,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(models.Model):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text=t3 + t4
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Категория'
    )
    is_published = models.BooleanField(
        default=True,
        blank=False,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено'
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )

    def __str__(self):
        return f'{self.author.username} — {self.text[:20]}'

    class Meta:
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
