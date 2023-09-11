import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

    def setUp(self):
        self.guest_client = Client()
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Начальный пост',
        )

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Пост для проверки работы формы'
        }
        response = self.user_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # проверка перенаправления на страницу профиля после отправки поста
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user})
        )
        # Проверка увеличения числа постов на 1
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверка создания поста с заданными данными
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Пост для проверки работы формы'
            ).exists()
        )

    def test_edit_post(self):
        test_id = 1
        new_form_data = {
            'text': 'Измененный пост'
        }
        self.user_client.post(
            reverse('posts:post_edit', args=(test_id,)),
            data=new_form_data,
            follow=True
        )
        self.assertEqual(Post.objects.get(id=test_id).text,
                         'Измененный пост')

    def test_create_post_guest_impossible(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Пост неавторизованного пользователя'
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # перенаправления на страницу авторизации при попытке отправки поста
        self.assertRedirects(response, '/auth/login/?next=/create/')
        # Проверка что число постов не увеличилось
        self.assertEqual(Post.objects.count(), post_count)
        # Проверка что новый пост не появился
        self.assertFalse(
            Post.objects.filter(
                text='Пост неавторизованного пользователя2'
            ).exists()
        )

    def test_edit_post_guest_client_impossible(self):
        test_id = 1
        new_form_data = {
            'text': 'Гость изменил пост'
        }
        self.guest_client.post(
            reverse('posts:post_edit', args=(test_id,)),
            data=new_form_data,
            follow=True
        )
        # Проверка что гостю не удалось изменить пост
        self.assertNotEqual(Post.objects.get(id=test_id).text,
                            'Гость изменил пост')
        # Проверка что пост остался в изначальном состояни
        self.assertEqual(Post.objects.get(id=test_id).text,
                         'Начальный пост')
        # Гость был перенаправлен на страницу авторизации
        response = self.guest_client.post(
            reverse('posts:post_edit', args=(test_id,)),
            data=new_form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{test_id}/edit/')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreationImagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_post_with_image(self):
        count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверка работы редиректа
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )
        # Проверка увеличения числа постов
        self.assertEqual(Post.objects.count(), count + 1)
        # Проверка существования созданной записи
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )

    def test_only_image_could_be_uploaded_in_post_form(self):
        """Проверка невозможности загрузки не-картинок в форму"""
        uploaded = SimpleUploadedFile(
            name='file.txt',
            content='some text'.encode(),
            content_type='text/plain'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        error_text = ('Загрузите правильное изображение. '
                      'Файл, который вы загрузили, поврежден '
                      'или не является изображением.')
        self.assertFormError(response, 'form', 'image', errors=error_text)
