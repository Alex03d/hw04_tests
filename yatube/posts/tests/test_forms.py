from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostFormTexts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        # Создаем пользователя
        self.guest_user = User.objects.create_user(username='Auth')
        # клиент АВТОРИЗОВАННЫЙ
        self.authorized_client = Client()
        self.authorized_client.force_login(self.guest_user)


    def test_create_post(self):
        """Валидная форма создает пост"""
        group = Group.objects.create(
            title='Тестовая группа для отправки',
            slug='test-slug-post',
            description='Тестовое описание группы не более 15 символов'
        )
        # Задание 1. При отправке валидной формы со страницы создания поста
        # reverse('posts:create_post') создаётся новая запись в базе данных
        posts_count = Post.objects.count()
        form_data_before = {
            'text': 'Тестовый заголовок для валидации',
            'author': User.objects.filter(username='Auth'),
            'group': group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_before,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Auth'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что создалась нужная запись
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок для валидации',
                id=1,
            ).exists()
        )
