from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_create_post_form(self):
        """Новый пост создается с помощью формы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertTrue(Post.objects.filter(
            group__slug='test-slug',
            text='Новый пост',
        ).exists())

        def test_edit_post_form(self):
            """Пост изменяется с помощью формы"""
            test_post = Post.objects.create(
                author=self.user,
                text='Тестовый пост',
            )
            form_data = {
                'text': 'Измененный пост',
                'group': self.group.id,
            }
            posts_count = Post.objects.count()
            response = self.author_client.post(
                reverse('posts:post_create'),
                kwargs={'post_id': test_post.pk},
                data=form_data,
                follow=True
            )
            self.assertEqual(Post.objects.count(), posts_count + 1)
            self.assertRedirects(response, reverse(
                'posts:post_detail',
                kwargs={'post_id': test_post.pk}))
            self.assertTrue(Post.objects.filter(
                group__slug='test-slug',
                text='Новый пост',
            ).exists())
