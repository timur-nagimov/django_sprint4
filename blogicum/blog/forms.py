from django import forms

from .models import Post, Comment


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
