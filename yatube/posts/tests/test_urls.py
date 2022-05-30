from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class GroupPostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.user_not_author = User.objects.create_user(username='NotAuthor')

        cls.urls = (
            ('posts:group_posts', (cls.group.slug,), 'posts/group_list.html'),
            ('posts:index', None, 'posts/index.html'),
            ('posts:profile', (cls.user,), 'posts/profile.html'),
            ('posts:post_detail', (cls.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (cls.post.id,), 'posts/create_post.html'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """reverse_name страниц используют соответствующий шаблон"""
        for url, args, template in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_exist_at_desired_location(self):
        """Страницы, доступные авторизованному пользователю"""
        for url, args, _ in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        else:
            response = self.author_client.get('/page_doesnt_exist/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_page_redirects_not_author_on_post_page(self):
        """Страница редактирования поста отправит неАвтора на страницу поста"""
        self.author_client.force_login(self.user_not_author)
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        self.assertRedirects(response, '/posts/1/')

    def test_post_create_page_redirects_not_author_on_post_page(self):
        """Страница создания поста перенаправит неАвтора на страницу поста"""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, '/auth/login/?next=/create/')
