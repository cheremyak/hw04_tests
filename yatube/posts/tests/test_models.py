from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group
        test_str = {
            post: 'Тестовый пост',
            group: 'Тестовая группа',
        }
        for value, expected in test_str.items():
            with self.subTest(value=value):
                self.assertEqual(str(post)[:15], post.text)
                self.assertEqual(str(group), group.title)
