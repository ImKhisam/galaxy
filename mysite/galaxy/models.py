from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField


class CustomUser(AbstractUser):
    is_confirmed = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='username')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('personal_acc', kwargs={'acc_slug': self.slug})


class Video(models.Model):
    title = models.CharField(max_length=100)
    added = models.DateTimeField(auto_now_add=True)
    url = EmbedVideoField()

    def __str__(self):
        return self.title

