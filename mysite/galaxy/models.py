from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_confirmed = models.BooleanField(default=False)
    #slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")