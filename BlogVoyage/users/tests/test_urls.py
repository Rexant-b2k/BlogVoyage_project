from django.contrib.auth import get_user_model
from django.test import Client, TestCase

# from ..models import Group, Post

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.users_urls_dict = {
            'login/': 'users/login.html',
            'signup/': 'users/signup.html',
            'password_change/': 'users/password_change_form.html',
            'password_change_done/': 'users/password_change_done.html',
            'password_reset/': 'users/password_reset_form.html',
            'password_reset/done/': 'users/password_reset_done.html',
            'reset/done/': 'users/password_reset_complete.html',
            'logout/': 'users/logged_out.html',
        }

    def test_urls_exists(self):
        for address in self.users_urls_dict.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(f'/auth/{address}')
                self.assertEqual(response.reason_phrase, 'OK')

    def test_urls_uses_correct_template(self):
        for address, templates in self.users_urls_dict.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(f'/auth/{address}')
                self.assertTemplateUsed(response, templates)
