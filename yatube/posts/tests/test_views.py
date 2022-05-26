from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
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
        cls.wrong_group = Group.objects.create(
            title='Тестовое название группы 2',
            slug='test-slug2',
            description='Тестовое описание группы 2'
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_with_posts_show_correct_context(self):
        """Шаблоны index, group_list и profile сформированы
        с правильным контекстом.
        """
        templates_page_names = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author}),
        }
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertIn(self.post, response.context.get('page_obj'))

    def test_group_posts_context(self):
        """Шаблон группы сформирован с правильным контекстом"""
        response = self.author_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group'), self.post.group)

    def test_author_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context.get('author'), self.user)
    
    def test_both_profile_and_group_show_correct_context(self):
        """Шаблоны group_posts и  profile сформированы
        с правильным контекстом
        """
        templates_page_names = [
            ('posts:group_posts', 'group', self.group.slug),
            ('posts:profile', 'author', self.user.id),
        ]
        for page, context_name, expected in templates_page_names:
            reverse_name = reverse(page, args=expected)
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(response.context.get(context_name), expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_new_post_not_in_a_wrong_group(self):
        """Пост не появляется в не своей группе"""
        response = self.author_client.get(
            reverse('posts:group_posts', kwargs={
                'slug': self.wrong_group.slug
            })
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))
