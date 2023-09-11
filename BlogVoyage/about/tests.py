from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.about_pages = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_exists(self):
        for address in self.about_pages.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_about_uses_correct_templates(self):
        for address, template in self.about_pages.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
