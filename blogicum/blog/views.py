from typing import Any

from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    UpdateView,
    ListView,
    CreateView,
    DetailView,
    DeleteView
)

from blogicum.forms import UserUpdateForm
from .constants import MAIN_PAGE_MAX_POSTS
from .models import Post, Category, Comment
from .forms import CreatePostForm, CreateCommentForm


User = get_user_model()


class PaginatorListMixin:
    model = Post
    paginate_by = MAIN_PAGE_MAX_POSTS


class BlogListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        now = timezone.now()
        # Фильтруем записи:
        # опубликованные и с датой публикации не позднее текущего времени
        return Post.objects.filter(is_published=True,
                                   pub_date__lte=now,
                                   category__is_published=True
                                   )


class ProfileListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'

    def get_user(self) -> User:
        # Получаем username из URL или используем имя текущего пользователя
        username = self.kwargs.get('username') or self.request.user.username
        return get_object_or_404(User, username=username)

    def get_queryset(self):
        user = self.get_user()
        return Post.objects.filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context


class CategoryListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('category_slug')
        context['category'] = Category.objects.get(slug=category)
        return context

    def get_queryset(self):
        now = timezone.now()
        category = self.kwargs.get('category_slug')
        get_object_or_404(Category, slug=category,
                          is_published=True)
        return Post.objects.filter(category__slug=category,
                                   is_published=True,
                                   pub_date__lte=now)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = CreatePostForm

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})

    def form_valid(self, form):
        form.instance.author_id = self.request.user.pk
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        post = self.get_object()
        category_status = post.category.is_published

        now = timezone.now()
        pub_date = post.pub_date

        # Проверяем, является ли пользователь
        # автором поста или пост опубликован
        if (not post.is_published
            or not category_status
                or pub_date > now) and post.author != request.user:
            # Если пользователь не автор и пост не опубликован,
            # показываем 404 ошибку
            raise Http404("Вы не можете просматривать этот пост")

        # Возвращаем ответ от родительского метода
        return response


class PostUpdateView(UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_id)

        if post.author.pk != request.user.pk:
            return redirect('blog:post_detail', pk=post_id)

        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreatePostForm(instance=self.object)
        return context

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('pk')
        user_id = self.request.user.pk
        return get_object_or_404(Post, pk=post_id, author=user_id)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def get_object(self, queryset=None):
        comment_id = self.kwargs['comment_id']
        user_id = self.request.user.pk

        return get_object_or_404(Comment, pk=comment_id, author=user_id)


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def get_object(self, queryset=None):
        # Получаем ID комментария из аргументов URL
        comment_id = self.kwargs['comment_id']
        user_id = self.request.user.pk

        return get_object_or_404(Comment, pk=comment_id, author=user_id)


@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=pk)
    form = CreateCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)

        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', pk=pk)
