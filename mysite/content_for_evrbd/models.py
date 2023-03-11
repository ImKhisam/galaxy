import os
from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField


def content_file_name(instance, filename):
    return '/'.join(['bb', instance.year, filename])


class BritishBulldog(models.Model):
    classes = models.CharField(max_length=255, verbose_name='Class')
    year = models.CharField(max_length=255, verbose_name='Year')
    content = models.FileField(upload_to=content_file_name)
    audio = models.FileField(upload_to=content_file_name, blank=True)

    def __str__(self):
        return self.classes

    class Meta:
        ordering = ['year', 'classes']


class Video(models.Model):
    title = models.CharField(max_length=100)
    added = models.DateTimeField(auto_now_add=True)
    url = EmbedVideoField()

    def __str__(self):
        return self.title