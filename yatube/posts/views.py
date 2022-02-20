from http.client import HTTPResponse
from xml.etree.ElementTree import Comment
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, CreateView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User, Comment
from .utils import paginator_page


class IndexListView(ListView):
    template_name = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group')
    context_object_name = 'page_obj'

    def get(self, request, *args, **kwargs):
        self.page = self.request.GET.get('page')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        paginator = Paginator(self.post_list, settings.SHOWING_POSTS)
        return paginator.get_page(self.page)


class GroupListView(ListView):
    template_name = 'posts/group_list.html'
    context_object_name = 'page_obj'

    def get(self, request, *args, **kwargs):
        self.page = self.request.GET.get('page')
        slug = kwargs['slug']
        self.group = get_object_or_404(Group, slug=slug)
        self.group_list = self.group.posts.select_related('author')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        paginator = Paginator(self.group_list, settings.SHOWING_POSTS)
        return paginator.get_page(self.page)

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context


class ProfileListView(ListView):
    template_name = 'posts/profile.html'
    context_object_name = 'page_obj'

    def get(self, request, *args, **kwargs):
        self.page = self.request.GET.get('page')
        username = kwargs['username']
        self.author = get_object_or_404(User, username=username)
        self.profile_list = self.author.posts.select_related('group')
        self.following = (
            request.user.is_authenticated
            and self.author.following.filter(user=request.user).exists()
        )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        paginator = Paginator(self.profile_list, settings.SHOWING_POSTS)
        return paginator.get_page(self.page)

    def get_context_data(self, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)
        context['author'] = self.author
        context['following'] = self.following
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'target_post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        target_post = context.get('target_post')
        comments = target_post.comments.all()
        context['form'] = CommentForm()
        context['comments'] = comments
        return context


@method_decorator(login_required, name="dispatch")
class PostCreateView(CreateView):
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect('posts_page:profile', form.instance.author.username)


@method_decorator(login_required, name="dispatch")
class PostEditView(UpdateView):
    model = Post
    template_name = 'posts/create_post.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        self.post_id = self.kwargs.get('post_id')

        if request.user.posts.filter(id=self.post_id).exists():
            return super().get(request, *args, **kwargs)

        return redirect('posts:post_detail', self.post_id)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.post_id
        context['is_edit'] = True
        return context

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('posts:post_detail', kwargs={'post_id': post_id})


@method_decorator(login_required, name="dispatch")
class AddCommentView(CreateView):
    model = Comment
    template_name = 'posts/post_detail.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['post_id']
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('posts:post_detail', kwargs={'post_id': post_id})


@method_decorator(login_required, name="dispatch")
class FollowListView(ListView):
    """Лента подписки"""
    model = Follow
    template_name = 'posts/follow.html'
    context_object_name = 'page_obj'

    def get(self, request, *args, **kwargs):
        self.page = self.request.GET.get('page')
        self.follow_list = Post.objects.filter(
            author__following__user=self.request.user
        )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        paginator = Paginator(self.follow_list, settings.SHOWING_POSTS)
        return paginator.get_page(self.page)


@method_decorator(login_required, name="dispatch")
class ProfileFollowView(View):
    """Подписка на автора"""
    model = Follow
    template_name = 'posts/profile.html'

    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        if request.user.id != author.id:
            Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts_page:profile', author)


@method_decorator(login_required, name="dispatch")
class ProfileUnfollowView(View):
    """Отписка от автора"""
    model = Follow
    template_name = 'posts/profile.html'

    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        if request.user.id != author.id:
            Follow.objects.filter(user=request.user, author=author).delete()

        return redirect('posts_page:profile', username)
