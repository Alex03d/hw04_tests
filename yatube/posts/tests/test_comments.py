import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import User, Group, Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author_post,
            text='Тестовый комментарий'
            ),

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.simple_user)
        self.author_post = Client()
        self.author_post.force_login(PostURLTest.author_post)

    def test_comment_in_post_detail_page_show_exist(self):
        responses = {
            'post_detail': self.authorized_client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.id}
                )
            )
        }

        for response in responses.values():
            first_object = response.context['comments'][0]
            self.assertIsNotNone(first_object)
            form_object = response.context['form']
            self.assertIsNotNone(form_object)
            self.assertTrue(
                Comment.objects.filter(
                    text='Тестовый комментарий'
                ).exists())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
