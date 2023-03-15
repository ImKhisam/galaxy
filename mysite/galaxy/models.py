from autoslug import AutoSlugField
from django import forms
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


def content_file_name_test(instance, filename):
    return '/'.join(['olymp', instance.year, instance.stage, filename])


class OlympWay(models.Model):
    School_stage = 'School stage'
    Municipal_stage = 'Municipal stage'
    Region_stage = 'Region stage'
    Final_stage = 'Final stage'
    choices_in_stage = [
        (School_stage, 'School stage'),
        (Municipal_stage, 'Municipal stage'),
        (Region_stage, 'Region stage'),
        (Final_stage, 'Final stage'),
    ]

    year = models.CharField(max_length=255, verbose_name='Year')
    stage = models.CharField(max_length=255, verbose_name='Stage', choices=choices_in_stage)
    classes = models.CharField(max_length=255, verbose_name='Class')
    task = models.FileField(upload_to=content_file_name_test)
    answer = models.FileField(upload_to=content_file_name_test, blank=True)
    audio = models.FileField(upload_to=content_file_name_test, blank=True)
    script = models.FileField(upload_to=content_file_name_test, blank=True)

    def __str__(self):
        return f"{self.year}, {self.stage}, {self.classes}"

    class Meta:
        ordering = ['year', 'stage']


class Tests(models.Model):
    GSE = 'GSE'
    USE = 'USE'
    choices_in_type = [
        (GSE, 'GSE'),
        (USE, 'USE'),
    ]
    Listening = 'Listening'
    Reading = 'Reading'
    Grammar = 'Grammar and Vocabulary'
    Writing = 'Writing'
    Speaking = 'Speaking'
    choices_in_part = [
        (Listening, 'Listening'),
        (Reading, 'Reading'),
        (Grammar, 'Grammar'),
        (Writing, 'Writing'),
        (Speaking, 'Speaking'),
    ]
    type = models.CharField(max_length=255, verbose_name='Type of exam', choices=choices_in_type)
    part = models.CharField(max_length=255, verbose_name='Part of exam', choices=choices_in_part)
    test_num = models.IntegerField()

    def __str__(self):
        return f"{self.type}, {self.part}, {self.pk}"

    class Meta:
        ordering = ['type', 'part']


class Questions(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    cost = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    question_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.test}, Q{self.question_number}"


class Answers(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    is_true = models.BooleanField(default=False)


