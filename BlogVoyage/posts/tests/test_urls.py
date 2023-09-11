from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='Тестовый пост',
            id=100,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author_user)
        self.post_urls = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/posts/100/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def tearDown(self):
        cache.clear()

    def test_all_pages_exists(self):
        for address in self.post_urls.keys():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_pages_required_login_do_redirect(self):
        post_urls_req_login = {
            '/posts/100/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address in post_urls_req_login.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_post_edit_required_author(self):
        expected_status_codes = {
            self.guest_client: 302,
            self.authorized_client: 302,
            self.author_client: 200,
        }
        for client, exp_code in expected_status_codes.items():
            with self.subTest(client=client):
                response = client.get('/posts/100/edit/')
                self.assertEqual(response.status_code, exp_code)

    def test_post_edit_redirect(self):
        non_author_users_redirect_addr = {
            self.guest_client: '/auth/login/?next=/posts/100/edit/',
            self.authorized_client: '/posts/100/',
        }
        for client, address in non_author_users_redirect_addr.items():
            with self.subTest(client=client):
                response = client.get('/posts/100/edit/', follow=True)
                self.assertRedirects(response, address)

    def test_unexpected_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        # Проверка использования кастомного шаблона для ошибки 404
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        for address, template in self.post_urls.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
