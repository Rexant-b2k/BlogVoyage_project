from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from BlogVoyage.settings import POSTS_PER_PAGE

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post

User = get_user_model()


class PaginatorViewTest(TestCase):
    NUM_OF_POSTS = 14

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='peggie')
        cls.group = Group.objects.create(
            title='Группа тестирования пагинации',
            slug='Paginator_group',
            description='Тестовое описание'
        )
        for _ in range(cls.NUM_OF_POSTS):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )

    def setUp(self):
        cache.clear()
        self.paginator_pages = (
            '',
            '/group/Paginator_group/',
            '/profile/peggie/',
        )
        self.guest = Client()

    def test_paginator_first_page_contains_10_posts(self):
        """Проверяем что paginator работает на всех страницах,
        использующих пагинацию и возвращает первые 10 элементов"""
        for page in self.paginator_pages:
            with self.subTest(page=page):
                response = self.guest.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_PAGE)

    def test_paginator_second_page_contains_rest_posts(self):
        """Проверяем что paginator корректно возвращает оставшиеся элементы
        на вторую страницу"""
        for page in self.paginator_pages:
            with self.subTest(page=page):
                response = self.guest.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.NUM_OF_POSTS - POSTS_PER_PAGE)


class PostsPagesTests(TestCase):
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
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.author_user)
        self.guest_client = Client()

    def test_pages_uses_correct_templates(self):
        """Проверка использования корректных шаблонов"""
        group = self.group.slug
        user = self.author_user
        post_urls = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             args=(group,)),
            'posts/profile.html': reverse('posts:profile', args=(user,)),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args=(self.post.id,)),
            'posts/create_post.html': reverse('posts:post_create'),

        }
        for template, address in post_urls.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_post_uses_correct_template(self):
        """Проверка использования корректного шаблона для post_edit"""
        response = self.author_client.get(reverse('posts:post_edit',
                                                  args=(self.post.id,)))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_show_correct_context(self):
        """Проверка передаваемого контекста для главной страницы"""
        response = self.guest_client.get(reverse('posts:index'))
        context = ['title', 'text', 'page_obj']
        for context_element in context:
            with self.subTest(field=context_element):
                self.assertIn(context_element, response.context)
        context_fields = {
            'title': 'Последние обновления на сайте',
            'text': 'Последние обновления на сайте',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIn(value, response.context)
                field = response.context.get(value)
                self.assertEqual(field, expected)

    def test_group_list_show_correct_context(self):
        """Проверка передаваемого контекста для страницы групп"""
        response = self.guest_client.get(reverse('posts:group_list',
                                                 args=(self.group.slug,)))
        context = ['group', 'page_obj']
        for context_element in context:
            with self.subTest(field=context_element):
                self.assertIn(context_element, response.context)
        field = response.context.get('group')
        self.assertEqual(field, self.group)

    def test_profile_show_correct_context(self):
        """Проверка передаваемого контекста для профиля пользователя"""
        response = self.guest_client.get(reverse('posts:profile',
                                                 args=(self.author_user,)))
        context = ['author', 'page_obj']
        for context_element in context:
            with self.subTest(field=context_element):
                self.assertIn(context_element, response.context)
        field = response.context.get('author')
        self.assertEqual(field, self.author_user)

    def test_post_detail_show_correct_content(self):
        """Проверяем что post_detail возвращает один конкретный пост
        с указанным id"""
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(response.context['post'].id, self.post.id)

    def test_post_create_returns_create_form(self):
        """Проверяем контекст create_form и использование формы
        класса PostForm"""
        response = self.author_client.get(reverse('posts:post_create'))
        context_fields = {
            'is_edit': False,
            'title': 'Добавить запись',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIn(value, response.context)
                field = response.context.get(value)
                self.assertEqual(field, expected)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_create_form_redirects_unathorized_client(self):
        """Проверяем что неавторизованный клиент будет перенаправлен
        на страницу авторизации"""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_returns_create_form(self):
        """Проверяем контекст edit_form и использование формы
        класса PostForm"""
        response = self.author_client.get(reverse('posts:post_edit',
                                                  args=(self.post.id,)))
        context_fields = {
            'is_edit': True,
            'title': 'Редактировать запись',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIn(value, response.context)
                field = response.context.get(value)
                self.assertEqual(field, expected)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_create_form_redirects_non_author(self):
        """Проверяем перенаправление клиента, не являющегося автором
        поста"""
        pid = self.post.id
        user = User.objects.create_user(username='second')
        authorized_user_client = Client()
        authorized_user_client.force_login(user)
        response = self.guest_client.get(reverse('posts:post_edit',
                                                 args=(pid,)))
        self.assertRedirects(response, f'/auth/login/?next=/posts/{pid}/edit/')
        response = authorized_user_client.get(reverse('posts:post_edit',
                                                      args=(pid,)))
        self.assertRedirects(response, f'/posts/{pid}/')

    def test_paginator_pages_show_correct_post_context(self):
        """Проверка содержимого постов на страницах с пагинатором"""
        paginator_pages = (
            '',
            '/group/test_slug/',
            '/profile/auth/',
        )
        for page in paginator_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                test_post = response.context['page_obj'][0]
                self.assertEqual(test_post.author.get_username(), 'auth')
                self.assertEqual(test_post.text, 'Тестовый пост')
                self.assertEqual(test_post.group.title, 'Тестовая группа')


class PostsCreationTests(TestCase):
    NUM_OF_POSTS = 5

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user('user1')
        cls.user2 = User.objects.create_user('user2')
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='gr1',
            description='Тестгруппа 1'
        )
        cls.group2 = Group.objects.create(
            title='group2',
            slug='gr2',
            description='group 2'
        )
        """Создание набора из 5 постов для группы 1, user1"""
        for _ in range(cls.NUM_OF_POSTS):
            cls.post = Post.objects.create(
                author=cls.user1,
                text='Тестовый пост группы 1',
                group=cls.group1
            )
        """Создание поста группы 2, user2"""
        Post.objects.create(
            author=cls.user2,
            text='Тестовый пост группы 2',
            group=cls.group2
        )

    def setUp(self):
        self.guest_client = Client()

    def test_group1_contains_only_group_posts(self):
        """Проверка что страница группы содержит только те посты,
        что принадлежат этой группе (5 шт)"""
        response = self.guest_client.get(reverse('posts:group_list',
                                                 args=('gr1',)))
        self.assertIn('page_obj', response.context)
        count = len(response.context['page_obj'])
        self.assertEqual(count, 5)
        for post in response.context['page_obj']:
            with self.subTest(post=post.text):
                self.assertEqual(post.group.title, 'Тестовая группа 1')

    def test_profile_user1_containt_only_author_posts(self):
        """Проверка что профиль пользователя содержит посты только
        автора user1 (5 шт)"""
        response = self.guest_client.get(reverse(
            'posts:profile', args=('user1',))
        )
        self.assertIn('page_obj', response.context)
        count = len(response.context['page_obj'])
        self.assertEqual(count, 5)
        for post in response.context['page_obj']:
            with self.subTest(post=post.text):
                self.assertEqual(post.author.get_username(), 'user1')

    def test_new_post_is_included_in_proper_pages(self):
        """Проверка правильности привязки последнего созданного поста
        на странице группы 2 и в профиле пользователя 2"""
        pages_contain_posts = (
            '/group/gr2/',
            '/profile/user2/',
        )
        for page in pages_contain_posts:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                count = len(response.context['page_obj'])
                self.assertEqual(count, 1)
                post = response.context['page_obj'][0]
                self.assertEqual(post.author.get_username(), 'user2')
                self.assertEqual(post.text, 'Тестовый пост группы 2')
                self.assertEqual(post.group.title, 'group2')
        """Встречная проверка страницы группы 1 и профиля пользователя 1
        там новый пост фигурировать не должен"""
        opposite_pages = ('/group/gr1/', '/profile/user1/')
        for page in opposite_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                for post in response.context['page_obj']:
                    with self.subTest(post=post):
                        self.assertNotEqual(post.author.get_username(),
                                            'user2')
                        self.assertNotEqual(post.text,
                                            'Тестовый пост группы 2')
                        self.assertNotEqual(post.group.title, 'group2')


class CommentCreationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.guest_client = Client()

    def test_post_detail_page_returns_correct_comment_form(self):
        """Проврка отображения корректной формы на странице поста"""
        response = self.user_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        comment_form = response.context.get('form')
        # Проверка переданной формы
        self.assertIsInstance(comment_form, CommentForm)

    def test_authorized_users_could_comment(self):
        """Проверка отправки комментариев
        авторизованным пользователем"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий авторизованного пользователя'
        }
        # Отправка комментария
        response = self.user_client.post(reverse(
            'posts:add_comment',
            args=(self.post.id,),),
            data=form_data,
            follow=True
        )
        # Проверка перенаправления после успешного комментария
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     args=(self.post.id,)))
        # Проеврка увеличения числа комментариев на 1
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
        )

    def test_guest_user_cannot_comment(self):
        """Проверка невозможности отправки комментариев
        гостевым пользователем"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий неавторизованного пользователя'
        }
        # Отправка комментария
        response = self.guest_client.post(reverse(
            'posts:add_comment',
            args=(self.post.id,),),
            data=form_data,
            follow=True
        )
        # Проверка перенаправления на страницу авторизации
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        # Проверка что число комментариев не увеличилось
        self.assertEqual(
            Comment.objects.count(),
            comments_count,
        )

    def test_added_comment_exists_on_post_page(self):
        """Проверка появления комментария на странице поста"""
        form_data = {
            'text': 'Комментарий'
        }
        self.user_client.post(reverse(
            'posts:add_comment',
            args=(self.post.id,),),
            data=form_data,
            follow=True
        )
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        comments = response.context.get('comments')
        self.assertEqual(comments[0].text, 'Комментарий')


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='test_post',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_index_cache(self):
        """Проверка работы кэширования главной страницы"""
        # Изначальная проверка наличия поста
        inital_response = self.guest_client.get(reverse('posts:index'))
        self.assertIn(self.post.text, inital_response.content.decode())
        self.post.delete()
        # Проврка наличия поста даже после удаления
        after_del_resp = self.guest_client.get(reverse('posts:index'))
        self.assertIn(self.post.text, after_del_resp.content.decode())
        self.assertEqual(inital_response.content, after_del_resp.content)
        cache.clear()
        # Исчезновение поста после очистки кэша
        after_clear_resp = self.guest_client.get(reverse('posts:index'))
        self.assertNotIn(self.post.text, after_clear_resp.content.decode())
        self.assertNotEqual(after_clear_resp.content, after_del_resp.content)
