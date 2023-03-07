import os
from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField


class Video(models.Model):
    title = models.CharField(max_length=100)
    added = models.DateTimeField(auto_now_add=True)
    url = EmbedVideoField()

    def __str__(self):
        return self.title