from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group, User


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
        templates_pages_names = [
            ('posts/index.html',
             reverse('posts:index')),
            ('posts/group_list.html',
             reverse('posts:group_posts', kwargs={'slug': 'test-slug'})),
            ('posts/profile.html',
             reverse(
                 'posts:profile',
                 kwargs={'username': self.post.author.username})
             ),
            ('posts/post_detail.html',
             reverse('posts:post_detail', kwargs={'post_id': self.post.id})),
            ('posts/create_post.html',
             reverse('posts:post_edit', kwargs={'post_id': self.post.id})),
            ('posts/create_post.html', reverse('posts:post_create'))]

        for template, reverse_name in templates_pages_names:
            return template, reverse_name
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_correct_context(self):
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
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=Group.objects.get(slug='test_group'),
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
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
        Post.objects.create(
            text='Текстовый пост с группой',
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
                    kwargs={'username': 'author_post'}))
        }
        for response in responses.values():
            inner_response = response
            first_object = inner_response.context['page_obj'][0]
            post_text_0: str = first_object.text
            post_author_0 = first_object.author
            post_group_0 = first_object.group
            self.assertEqual(post_text_0, 'Текстовый пост с группой')
            self.assertEqual(
                post_author_0,
                User.objects.get(username='author_post'),
            )
            self.assertEqual(
                post_group_0,
                Group.objects.get(
                    title='Тестовая группа',
                )
            )
