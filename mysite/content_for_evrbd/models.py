import os
from django.db import models
from django.urls import reverse

#module_dir = os.path.dirname(__file__)
#os.path.join(module_dir, 'media/2015.pdf')

def content_file_name(instance, filename):
    return '/'.join(['bb', instance.year, filename])

class BrittishBulldog(models.Model):
    classes = models.CharField(max_length=255, verbose_name='Class')
    year = models.CharField(max_length=255, verbose_name='Year')
    content = models.FileField(upload_to=content_file_name)
    audio = models.FileField(upload_to=content_file_name, blank=True)

    def __str__(self):
        return self.classes

    def get_absolute_url(self):
        return reverse('show_bb_year', kwargs={'bb_slug': self.year})

    class Meta:
        ordering = ['year', 'classes']