import os
from django.db import models

# pre_save function for Book class to update blank titles
# https://qna.habr.com/q/109793
from django.db.models.signals import pre_save
from django.dispatch import receiver


MULTIVOLUME_STORY = "MVS"
MULTIVOLUME_CYCLE = "MVC"
MULTIVOLUME_FALSE = "MVF"


def str_list_items(queryset, attribute_string=False, split_string=", "):
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
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.name


def upload_img_front(instance, filename):
    _, fext = os.path.splitext(filename)
    return "books/{}/front{}".format(instance.pk, fext)

def upload_img_side(instance, filename):
    _, fext = os.path.splitext(filename)
    return "books/{}/side{}".format(instance.pk, fext)


class Book(models.Model):
    MULTIVOLUME_CHOICES = [
        (MULTIVOLUME_STORY, "Один из нескольких томов"),
        (MULTIVOLUME_CYCLE, "Одна из нескольких книг серии"),
        (MULTIVOLUME_FALSE, "Самостоятельная книга"),
    ]

    title = models.CharField(max_length=100, blank=True)
    image_front = models.ImageField(upload_to=upload_img_front, blank=True)
    image_side = models.ImageField(upload_to=upload_img_side, blank=True)
    year_released = models.SmallIntegerField(blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    stories = models.ManyToManyField('Story', blank=True)

    comment = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)


    has_multivolume = models.CharField(
        max_length=3, choices=MULTIVOLUME_CHOICES, default=MULTIVOLUME_FALSE)
    multivolume = models.ForeignKey(
        'Story', on_delete=models.PROTECT, null=True, blank=True,
        default=None, related_name="volumes")
    volume_id = models.SmallIntegerField(default=0)


    def __str__(self): return self.title

    def multivolume_check(self):
        """Check is there any errors in book-story relationship:

        1. If the book is NOT a part of multibook story / book cycle, it must have
            - has_multivolume=MULTIVOLUME_FALSE,
            - volume_id=0,
            - multivolume=None.

        2. The book from book cycle:
            - has_multivolume=MULTIVOLUME_CYCLE,
            - volume_id>0,
            - is part of multivolume story (multivolume exists),
            - the book has a stor[-y|-ies] inside.

        3. The book is a part of multivolume story:
            - has_multivolume=MULTIVOLUME_STORY,
            - volume_id>0,
            - is part of multivolume story (multivolume exists),
            - the book has no story inside it.
        """
        if self.has_multivolume == MULTIVOLUME_FALSE:
            return self.volume_id == 0 and self.multivolume is None
        elif self.has_multivolume == MULTIVOLUME_CYCLE:
            return self.volume_id > 0 and not self.multivolume is None and self.stories.count() > 0
        else:
            return self.volume_id > 0 and not self.multivolume is None and self.stories.count() == 0
        return False

    def list_stories(self):
        # add:
        # isMultivol
        # isMultivolCycle
        return str_list_items(self.stories.all())


# https://qna.habr.com/q/109793
@receiver(pre_save, sender=Book)
def set_title(sender, instance, **kwargs):
    """Blank title autofilling"""
    if instance.title == "" and instance.multivolume_check():
        if instance.has_multivolume == MULTIVOLUME_STORY:
            instance.title = "{title}, Том {vol}.".format(
                title=instance.multivolume, vol=instance.volume_id)
        else:
            instance.title = "{title}".format(title=instance.stories.first())
            if not instance.multivolume is None:
                instance.title += " [{id}/{id_count}]".format(
                    id=instance.volume_id, id_count=instance.multivolume.volumes_count
                )
        instance.title += " <auto>"


class Story(models.Model):
    """The story can be:
        - a simple story with it's own author/authors,
        - a story of several volumes,
        - a books cycle, with a common name
            and single author / several authors / each bookwriter.
    """

    MULTIVOLUME_CHOICES = [
        (MULTIVOLUME_STORY, "Многотомник"),
        (MULTIVOLUME_CYCLE, "Цикл книг"),
        (MULTIVOLUME_FALSE, "Самостоятельное"),
    ]

    title = models.CharField(max_length=100)
    authors = models.ManyToManyField('Author', blank=True)
    genres = models.ManyToManyField(Genre, blank=True)

    is_multivolume = models.CharField(
        max_length=3, choices=MULTIVOLUME_CHOICES, default=MULTIVOLUME_FALSE)
    volumes_count = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        add = '' if self.is_multivolume == MULTIVOLUME_FALSE else \
            dict(self.MULTIVOLUME_CHOICES)[self.is_multivolume]
        return f'{self.list_authors()}, {add} "{self.title}"'
        # set([v.stories.first().authors.first() for v in a.volumes.all()])
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
