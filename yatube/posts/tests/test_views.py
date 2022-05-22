from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post

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
        cls.user2 = User.objects.create_user(username='NoNameAuthor2')
        cls.group2 = Group.objects.create(
            title='Тестовое название группы 2',
            slug='test-slug2',
            description='Тестовое описание группы 2'
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
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_with_posts_show_correct_context(self):
        """Шаблоны index, group_list и profile сформированы
        с правильным контекстом.
        """
        templates_page_names = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                first_object = response.context.get('page_obj')[settings.ZERO]
                post_group_0 = first_object.group.slug
                post_author_0 = first_object.author
                post_text_0 = first_object.text
                self.assertEqual(post_group_0, self.group.slug)
                self.assertEqual(post_author_0, self.post.author)
                self.assertEqual(post_text_0, self.post.text)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            )
        first_object = response.context.get('post')
        post_group_0 = first_object.group.slug
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_group_0, self.group.slug)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_id_0, self.post.id)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        def test_new_post_appears_on_pages(self):
            """Новый пост появляется на страницах index, group_list и profile,
            а так же в единственной групее
            """
            templates_page_names = {
                reverse('posts:group_posts',
                        kwargs={'slug': self.group2.slug}
                        ),
                reverse('posts:index'),
                reverse('posts:profile',
                        kwargs={'username': self.user2.username}
                        ),
            }
            post2 = Post.objects.create(
                text='Тестовый текст поста',
                author=self.user2,
                group=self.group2,
            )
            for reverse_name in templates_page_names:
                with self.subTest(reverse_name=reverse_name):
                    response = self.author_client.get(reverse_name)
                    first_object = response.context.get(
                        'page_obj'
                    )[settings.ZERO]
                    post_text_0 = first_object.text
                    post_author_0 = first_object.author
                    post_group_0 = first_object.group.slug
                    self.assertEqual(post_text_0, post2.text)
                    self.assertEqual(post_author_0, post2.author)
                    self.assertEqual(post_group_0, self.group2.slug)
