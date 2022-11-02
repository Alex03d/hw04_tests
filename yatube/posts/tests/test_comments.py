from django.test import Client, TestCase
from django.urls import reverse

from ..models import User, Group, Post, Comment


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        # cls.group = Group.objects.create(
        #     title='Тестовая группа',
        #     slug='test-slug',
        #     description='Тестовое описание',
        # )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )
        # cls.comment = Comment.objects.create(
        #     author=cls.author_post,
        #     text='Тестовый комментарий',
        # )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.simple_user)
        self.author_post = Client()
        self.author_post.force_login(PostURLTest.author_post)

    def test_comment_in_post_detail_page_show_exist(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий'
            ).exists()
        )
        # self.assertEqual(Comment.objects.count(), comments_count + 1)
        # self.assertRedirects(response, f'posts/{self.post.pk}')



# from django.test import Client, TestCase
#
# from yatube.posts.models import User, Group, Post, Comment
#
#
# class PostURLTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.author_post = User.objects.create_user(username='author_post')
#         cls.simple_user = User.objects.create_user(username='simple_user')
#         cls.group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test-slug',
#             description='Тестовое описание',
#         )
#         cls.post = Post.objects.create(
#             author=cls.author_post,
#             text='Текстовый пост',
#         )
#         cls.comment = Comment.objects.create(
#             author=cls.author_post,
#             text='Текстовый комментарий',
#         )
#
#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client = Client()
#         self.authorized_client.force_login(PostURLTest.simple_user)
#         # self.author_post = Client()
#         # self.author_post.force_login(PostURLTest.author_post)
#
#     def test_post_create_correct_appearance(self):
#         Post.objects.create(
#             text='Текстовый пост с группой',
#             author=User.objects.get(username='author_post'),
#             group=Group.objects.get(
#                 title='Тестовая группа',
#             )
#         )
#         Comment.objects.create(
#             text='Текстовый комментарий',
#             author=User.objects.get(username='author_post'),
#         )
#         responses = {
#             'post_detail': self.authorized_client.get(
#                 reverse(
#                     'posts:group_posts',
#                     kwargs={'slug': 'test-slug'})),
#             'profile': self.authorized_client.get(
#                 reverse(
#                     'posts:profile',
#                     kwargs={'username': 'author_post'}))
#         }
#         for response in responses.values():
#             inner_response = response
#             first_object = inner_response.context['page_obj'][0]
#             post_text_0: str = first_object.text
#             post_author_0 = first_object.author
#             post_group_0 = first_object.group
#             self.assertEqual(post_text_0, 'Текстовый пост с группой')
#             self.assertEqual(
#                 post_author_0,
#                 User.objects.get(username='author_post'),
#             )
#             self.assertEqual(
#                 post_group_0,
#                 Group.objects.get(
#                     title='Тестовая группа',
#                 )
#             )
