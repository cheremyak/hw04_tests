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
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.user1 = User.objects.create_user(username='NotAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

        def test_pages_uses_correct_template(self):
            templates_page_names = {
                reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                    'posts/group_list.html',
                reverse('posts:index'): 'posts/index.html',
                reverse(
                    'posts:profile', kwargs={'username': self.user.username}
                ): 'posts/profile.html',
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                    'posts/post_detail.html',
                reverse('posts:post_create'): 'posts/create_post.html',
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                    'posts/create_post.html',
            }
            for reverses, template in templates_page_names.items():
                with self.subTest(reverse_name=reverses, template=template):
                    response = self.author_client.get(reverses)
                    self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/NoNameAuthor/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url, template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_doesnt_exist_returns_404(self):
        """Переход на несуществующую страницу ведет к ошибке 404"""
        response = self.client.get('page_doesnt_exist/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_exist_at_desired_location(self):
        """Страницы, доступные неавторизованному пользователю"""
        pages_status = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/NoNameAuthor/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/page_doesnt_exist/': HTTPStatus.NOT_FOUND,
        }
        for page, status in pages_status.items():
            with self.subTest(page=page, status=status):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, status)

    def test_post_edit_page_exists_at_desired_location(self):
        """Страница редактирования поста доступна автору"""
        response = self.author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_redirects_not_author_on_post_page(self):
        """Страница редактирования поста отправит неАвтора на страницу поста"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')

    def test_post_create_page_exists_at_desired_location(self):
        """Страница создания поста доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_page_redirects_not_author_on_post_page(self):
        """Страница создания поста перенаправит неАвтора на страницу поста"""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')
