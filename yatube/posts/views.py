from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

SHOWING_POSTS: int = 10


def index(request):
    page_obj = paginator_page(
        Post.objects.select_related('author', 'group'),
        request.GET.get('page'), SHOWING_POSTS
    )
    template = 'posts/index.html'
    return render(request, template, {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator_page(
        group.posts.select_related('author'),
        request.GET.get('page'), SHOWING_POSTS
    )
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginator_page(
        author.posts.select_related('group'),
        request.GET.get('page'), SHOWING_POSTS
    )
    following = request.user.is_authenticated and author.following.filter(
        user=request.user
    ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    target_post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = target_post.comments.all()

    template = 'posts/post_detail.html'

    context = {
        'target_post': target_post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'

    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form})

    form = PostForm(request.POST, files=request.FILES or None)
    if not form.is_valid():
        return render(request, template, {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect(
        'posts_page:profile', form.instance.author.username
    )


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    target_post = get_object_or_404(Post, id=post_id)

    if target_post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=target_post
    )
    if not form.is_valid():
        is_edit: bool = True
        context = {
            'form': form,
            'post_id': post_id,
            'is_edit': is_edit
        }
        return render(request, template, context)
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    """Добавление комментариев к постам"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Лента подписки на авторов"""
    follow_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_page(
        follow_list, request.GET.get('page'), SHOWING_POSTS
    )
    context = {
        'page_obj': page_obj,
    }

    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)

    if request.user.id != author.id:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('posts_page:profile', author)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)

    if request.user.id != author.id:
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts_page:profile', username)


def paginator_page(queryset: QuerySet, page: int, showing_posts: int) -> Page:
    paginator = Paginator(queryset, showing_posts)
    return paginator.get_page(page)
