from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        cls.group = Group.objects.create(
            title='Тестовая гурппа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.simple_user)
        self.author_post = Client()
        self.author_post.force_login(PostURLTest.author_post)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': self.post.author.username}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_correct_context(self):
        """Тест шаблона post_create с правильными полями  формы"""
        response = self.author_post.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Test_User", )
        cls.group = Group.objects.create(
            title="тест-группа",
            slug="test_group",
            description="тестирование",
        )
        #  Создаём 13 тестовых записей
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=Group.objects.get(slug='test_group'),
            )

    def setUp(self):
        #  Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        #  Создаем авторизованый клиент
        self.authorized_client = Client()
        #  Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """По 10 постов на первой странице у index, group_list и profile"""
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """По 3 поста на второй странице index, group_list и profile"""
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.guest_client.get(template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.simple_user)
        self.author_post = Client()
        self.author_post.force_login(PostURLTest.author_post)

    def test_post_create_correct_appearance(self):
        """View-функция post_create верно создает пост и отображает его"""
        # создадим запись в БД
        Post.objects.create(
            text='Тестовый пост c группой',
            author=User.objects.get(username='author_post'),
            group=Group.objects.get(
                title='Тестовая группа',
            )
        )
        responses = {
            'index': self.authorized_client.get(
                reverse('posts:index')),
            'group_posts': self.authorized_client.get(
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': 'test-slug'})),
            'profile': self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': 'Auth'}))
        }
        for response in responses.values():
            inner_response = response(['page_obj'][0])
            first_object = inner_response.context['page_obj'][0]
            post_text_0 = first_object.text
            post_author_0 = first_object.author
            post_group_0 = first_object.group
            self.assertEqual(post_text_0, 'Тестовый пост c группой')
            self.assertEqual(
                post_author_0,
                *User.objects.filter(
                    username='Auth',
                ),
                User.objects.get(username='author_post'),
            )
            self.assertEqual(
                post_group_0,
                *Group.objects.filter(
                    title='Тестовая группа',
                )
            )

# class PostURLTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.author_post = User.objects.create_user(username='author_post')
#         cls.simple_user = User.objects.create_user(username='simple_user')
#         cls.group = Group.objects.create(
#             title='Тестовая гурппа',
#             slug='test-slug',
#             description='Тестовое описание',
#         )
#         cls.post = Post.objects.create(
#             author=cls.author_post,
#             text='Текстовый пост',
#         )
#
#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client = Client()
#         self.authorized_client.force_login(PostURLTest.simple_user)
#         self.author_post = Client()
#         self.author_post.force_login(PostURLTest.author_post)


# class PostURLTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.author_post = User.objects.create_user(username='author_post')
#         cls.simple_user = User.objects.create_user(username='simple_user')
#         cls.group = Group.objects.create(
#             title='Тестовая гурппа',
#             slug='test-slug',
#             description='Тестовое описание',
#         )
#         cls.post = Post.objects.create(
#             author=cls.author_post,
#             text='Текстовый пост',
#     )
#
#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client = Client()
#         self.authorized_client.force_login(PostURLTest.simple_user)
#         self.author_post = Client()
#         self.author_post.force_login(PostURLTest.author_post)
#
#     def test_urls_page_post_with_group(self):
#         urls_page_post_with_group = {
#             'posts/index.html': reverse('posts:index'),
#             'posts/group_list.html': reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
#             'posts/profile.html': reverse('posts:profile', kwargs={'username': self.post.author.username}),
#             'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
#             'posts/create_post.html': reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
#             'posts/create_post.html': reverse('posts:post_create'),
#         }
#
#         for url in urls_page_post_with_group:
#                 with self.subTest(url=url):
#                     response = self.guest_client.get(url)
#                     list_of_posts = response.context['page_obj']
#                     self.assertIn(PostsPagesTests.post, list_of_posts)

# self.assertIn('author', response.context)
# self.assertEqual(response.context['author'], TestPosts.user)
