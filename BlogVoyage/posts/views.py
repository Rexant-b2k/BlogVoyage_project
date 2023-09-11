from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from BlogVoyage.settings import CACHE_TIME, POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def get_page(request, post_list):
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(CACHE_TIME, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all().select_related('author', 'group')
    page_obj = get_page(request, post_list)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'text': title,
        'title': title,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User.objects.filter(username=username))
    page_obg = get_page(request, author.posts.all())
    following = False
    if not request.user.is_anonymous:
        if Follow.objects.filter(
            user=request.user,
            author=author
        ).exists():
            following = True
    context = {
        'page_obj': page_obg,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id
    )
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)

    template = 'posts/create_post.html'
    title = 'Добавить запись'
    context = {
        'form': form,
        'is_edit': False,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/create_post.html'
    title = 'Редактировать запись'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)

    context = {
        'form': form,
        'is_edit': True,
        'title': title,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = get_page(request, post_list)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=user, author=author).exists():
        return redirect('posts:follow_index')
    if user != author:
        follow = Follow(
            user=user,
            author=author,
        )
        follow.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author=get_object_or_404(
            User,
            username=username,
        ),
    )
    follow.delete()
    return redirect('posts:follow_index')
