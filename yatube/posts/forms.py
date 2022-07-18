from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        widgets = {
            "text": Textarea(
                attrs={"class": "form-control", "placeholder": "Текст нового поста"}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Текст нового комментарий",
                }
            ),
        }
