from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    is_confirmed = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='username')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('personal_acc', kwargs={'acc_slug': self.slug})


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


class Olymp(models.Model):
    classes = models.CharField(max_length=255, verbose_name='Class')
    year = models.CharField(max_length=255, verbose_name='Year')
    content = models.FileField(upload_to=content_file_name)
    audio = models.FileField(upload_to=content_file_name, blank=True)

    def __str__(self):
        return self.classes



