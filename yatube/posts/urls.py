from django.urls import path

from . import views
from .views import (GroupListView, IndexListView, PostCreateView,
                    PostDetailView, PostEditView, ProfileListView,
                    AddCommentView, FollowListView, ProfileFollowView,
                    ProfileUnfollowView)

app_name = 'posts_page'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('group/<slug:slug>/', GroupListView.as_view(), name='group_list'),
    path('profile/<str:username>/', ProfileListView.as_view(), name='profile'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/edit/', PostEditView.as_view(), name='post_edit'),
    path(
        'posts/<int:post_id>/comment/',
        AddCommentView.as_view(), name='add_comment'
    ),
    path('follow/', FollowListView.as_view(), name='follow_index'),
    #path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        ProfileFollowView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        ProfileUnfollowView.as_view(),
        name='profile_unfollow'
    ),
]
