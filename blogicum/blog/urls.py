from django.urls import include, path

from . import views

app_name = 'blog'

profile_patterns = [
    path('edit/',
         views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('',
         views.ProfileListView.as_view(),
         name='profile'),
    path('<str:username>/',
         views.ProfileListView.as_view(),
         name='profile'),
]

post_patterns = [
    path('create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('<int:pk>/comment/',
         views.add_comment,
         name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
]

urlpatterns = [
    path('',
         views.BlogListView.as_view(),
         name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
    path('profile/', include(profile_patterns)),
    path('posts/', include(post_patterns)),
]
