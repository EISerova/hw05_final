from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    list_editable = ("group",)
    search_fields = (
        "text",
        "slug",
    )
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupClass(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    list_editable = ("title", "slug", "description")
    empty_value_display = "без сообщества"


class CommentClass(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("author",)
    list_editable = ("text",)
    empty_value_display = "без комментариев"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupClass)
admin.site.register(Comment, CommentClass)
