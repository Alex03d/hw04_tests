from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, User, Post


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Test post'
        )
        Comment.objects.create(
            post=cls.post,
            author=cls.author_post,
            text='New comment'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentCreateFormTests.simple_user)

    def test_ability_to_post_a_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Comment check',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count)
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        response = self.client.get(reverse('posts:post_detail',
                                           kwargs={'post_id': self.post.id}
                                           ))
        newly_created_comment = response.context['comments'][0]
        self.assertEqual(str(newly_created_comment), 'Comment check')
