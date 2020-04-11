import os
from django.db import models

def str_list_items(queryset, attribute_string = False, split_string = ", "):
    """Get string of items divided by split_string.

    Attributes:
        queryset - items iterable
        attribute_string=False - item field which will be concatenated, 
            by default it will use str(item)
        split_string=", " - items divider

    Example:
        str_list_items(self.genres.all(), "name")
    """
    result = ""
    for _, item in enumerate(queryset):
        result += eval('item.' + attribute_string) if attribute_string else str(item)
        if _ <= len(queryset)-2:
            result += split_string
    return result


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.name


class Book(models.Model):

    def upload_img_front(self, instance, filename):
        fname, fext = os.path.splitext(filename)
        return "books/{}/front{}".format(instance.pk, fext)

    def upload_img_side(self, instance, filename):
        fname, fext = os.path.splitext(filename)
        return "books/{}/side{}".format(instance.pk, fext)

    title = models.CharField(max_length=100)
    image_front = models.ImageField(upload_to=upload_img_front, blank=True)
    image_side = models.ImageField(upload_to=upload_img_side, blank=True)
    year_released = models.SmallIntegerField()
    comment = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    stories = models.ManyToManyField('Story')

    # multivolume = models.ForeignKey('Book', on_delete=models.PROTECT, null=True, blank=True, default=None)

    def list_stories(self):
        return str_list_items(self.stories.all())


class Story(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField('Author')
    genres = models.ManyToManyField(Genre)
    year_published = models.SmallIntegerField(blank=True)

    def __str__(self):
        return f'"{self.title}" {self.list_authors()}'
    def list_authors(self):
        return str_list_items(self.authors.all(), "name_short")
    def list_genres(self):
        return str_list_items(self.genres.all(), "name")


class Author(models.Model):
    name_full = models.CharField(max_length=100, unique=True)
    name_short = models.CharField(max_length=50, blank=True, unique=True)
    country = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name_short
