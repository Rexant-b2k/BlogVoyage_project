from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.f_user = User.objects.create_user(username='fan')
        cls.uf_user = User.objects.create_user(username='notfan')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Пост только для фанатов!'
        )

    def setUp(self):
        self.f_client = Client()
        self.f_client.force_login(self.f_user)
        self.uf_client = Client()
        self.uf_client.force_login(self.uf_user)
        self.guest_client = Client()
        self.profile = reverse('posts:profile', args=(self.author,))

    def test_unathorized_user_cannot_follow(self):
        """Проверка что неавторизованный пользователь
        перенаправляется на страницу логина при подписке"""
        response = self.guest_client.get(
            reverse('posts:profile_follow', args=(self.author,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/auth/login/?next=/profile/author/follow/'
        )

    def test_auth_user_can_follow(self):
        """Проверка возможности подписаться и появления подписки"""
        response = self.f_client.get(reverse(
            'posts:profile_follow', args=(self.author,)
        ))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/follow/'
        )
        self.assertTrue(Follow.objects.filter(
            user=self.f_user,
            author=self.author
        ).exists()
        )

    def test_post_appeared_on_following_page(self):
        """Проверка появления поста отслеживаемого автора на
        странице подписки"""
        self.f_client.get(reverse(
            'posts:profile_follow', args=(self.author,)
        ))
        response = self.f_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_posts_are_not_appeared_for_unfollowing_user(self):
        """Проверка отсутствия поста неотслеживаемого автора"""
        response = self.uf_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context.get('page_obj'))
