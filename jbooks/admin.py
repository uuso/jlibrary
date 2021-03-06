from django.contrib import admin
from .models import Author, Story, Book, Publisher, Genre

admin.site.register(Genre)
admin.site.register(Publisher)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name_full", "country", )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_multivolume", "volumes_count",
                    "list_authors", "list_genres", )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "has_multivolume", "multivolume",
                    "volume_id", "list_stories", "multivolume_check")
