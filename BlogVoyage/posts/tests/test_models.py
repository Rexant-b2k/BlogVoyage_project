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
            text='Тестовый пост c оооооочень длинным именем',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_objects = {
            post: post.text[:post.TEXT_LIMIT_SYMB],
            group: group.title,
        }
        for object, expected in expected_objects.items():
            with self.subTest(object=object):
                self.assertEqual(expected, str(object))

    def test_post_verbose_names(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected
                )
        meta_verboses = {
            'verbose_name': 'Запись в блоге',
            'verbose_name_plural': 'Записи в блоге',
        }
        for field, expected in meta_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(post._meta, field), expected)

    def test_post_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Выберите группу',
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected
                )
