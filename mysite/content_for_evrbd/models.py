import os
from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField


def content_bb_name(instance, filename):
    return '/'.join(['bb', instance.year, filename])


class BritishBulldog(models.Model):
    classes = models.CharField(max_length=255, verbose_name='Class')
    year = models.CharField(max_length=255, verbose_name='Year')
    content = models.FileField(upload_to=content_bb_name)
    audio = models.FileField(upload_to=content_bb_name, blank=True)

    def __str__(self):
        return self.classes

    class Meta:
        ordering = ['year', 'classes']


def content_file_name_olymp(instance, filename):
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
    task = models.FileField(upload_to=content_file_name_olymp)
    answer = models.FileField(upload_to=content_file_name_olymp, blank=True)
    audio = models.FileField(upload_to=content_file_name_olymp, blank=True)
    script = models.FileField(upload_to=content_file_name_olymp, blank=True)
    stage_order = models.IntegerField(verbose_name='stage_order')
    classes_order = models.IntegerField(verbose_name='classes_order')

    def __str__(self):
        return f"{self.year}, {self.stage}, {self.classes}"

    class Meta:
        ordering = ['year', 'stage']


class Video(models.Model):
    title = models.CharField(max_length=100)
    added = models.DateTimeField(auto_now_add=True)
    url = EmbedVideoField()

    def __str__(self):
        return self.title


def content_quiz_name(instance, filename):
    return '/'.join(['quiz', filename])


class Quizzes(models.Model):
    title = models.CharField(max_length=100)
    quiz = models.FileField(upload_to=content_quiz_name)
    answer = models.FileField(upload_to=content_quiz_name)


def content_tutorial_name(instance, filename):
    return '/'.join(['tutorial', filename])


class TutorialFile(models.Model):
    Articles = 'Articles'
    Lessons = 'Lessons'
    Methodological = 'Methodological guidelines'
    Presentations = 'Classroom presentations'
    Materials = 'Teaching materials'
    choices_in_category = [
        (Articles, 'Articles'),
        (Lessons, 'Lessons'),
        (Methodological, 'Methodological guidelines'),
        (Presentations, 'Classroom presentations'),
        (Materials, 'Teaching materials'),
    ]
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to=content_tutorial_name)
    category = models.CharField(max_length=255, verbose_name='Category', choices=choices_in_category)
