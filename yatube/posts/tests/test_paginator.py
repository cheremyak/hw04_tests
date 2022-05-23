from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.paginator import Paginator

from posts.models import Group, Post

User = get_user_model()


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.posts_number = 55
        pile_of_posts = [Post(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост' + str(post))
            for post in range(cls.posts_number)
        ]
        Post.objects.bulk_create(pile_of_posts)
        cls.p = Paginator(pile_of_posts, settings.POSTS_LIMIT)

    def setUp(self):
        self.guest_client = Client()

    def test_first_two_pages_contain_ten_and_thirteen_records(self):
        """"""
        pages_with_pagination = {
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }
        for reverse_name in pages_with_pagination:
            response = self.guest_client.get(reverse_name)
            self.assertEqual(
                len(response.context['page_obj']),
                settings.POSTS_LIMIT
            )
            response = self.guest_client.get(
                reverse_name + '?page=' + str(self.p.num_pages)
            )
            self.assertEqual(
                len(response.context['page_obj']),
                self.p.count % settings.POSTS_LIMIT
            )
