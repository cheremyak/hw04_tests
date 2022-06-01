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
        cls.user_not_author = User.objects.create_user(username='NotAuthor')

        cls.urls = (
            ('posts:group_posts', (cls.group.slug,), 'posts/group_list.html',
             HTTPStatus.OK),
            ('posts:index', None, 'posts/index.html', HTTPStatus.OK),
            ('posts:profile', (cls.user,), 'posts/profile.html',
             HTTPStatus.OK),
            ('posts:post_detail', (cls.post.id,), 'posts/post_detail.html',
             HTTPStatus.OK),
            ('posts:post_create', None, 'posts/create_post.html',
             HTTPStatus.OK),
            ('posts:post_edit', (cls.post.id,), 'posts/create_post.html',
             HTTPStatus.OK),
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """reverse_name страниц используют соответствующий шаблон"""
        for url, args, template, status_code in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_exist_at_desired_location(self):
        """Страницы, доступные авторизованному пользователю"""
        for url, args, teplate, expected_status in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(response.status_code, expected_status)

    def test_post_edit_page_redirects_not_author_on_post_page(self):
        """Страница редактирования поста отправит неАвтора на страницу поста"""
        self.author_client.force_login(self.user_not_author)
        reverse_post_detail = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        )
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        self.assertRedirects(response, f'{reverse_post_detail}')

    def test_post_create_page_redirects_not_author_on_post_page(self):
        """Страница создания поста перенаправит неАвтора на страницу поста"""
        reverse_login = reverse('users:login')
        reverse_create = reverse('posts:post_create')
        response = self.guest_client.get(reverse_create)
        self.assertRedirects(response,
                             f'{reverse_login}?next={reverse_create}')
