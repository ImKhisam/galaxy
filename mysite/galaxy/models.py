from autoslug import AutoSlugField
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    role_choice = ((None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher'))
    role = models.CharField(max_length=100, choices=role_choice)
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
    test_num = models.IntegerField()
    type = models.CharField(max_length=255, verbose_name='Type of exam', choices=choices_in_type)
    part = models.CharField(max_length=255, verbose_name='Part of exam', choices=choices_in_part)

    def __str__(self):
        return f"{self.type}, {self.part}, Test №{self.pk}"

    class Meta:
        ordering = ['type', 'part']


class Questions(models.Model):
    single_choice_type = 'single_choice_type'
    match_type = 'match_type'
    input_type = 'input_type'
    choices_in_question_type = [
        (single_choice_type, 'single_choice_type'),
        (match_type, 'match_type'),
        (input_type, 'input_type')
    ]

    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    question_number = models.PositiveIntegerField()
    question_type = models.CharField(max_length=255, verbose_name='Type of question', choices=choices_in_question_type)

    def __str__(self):
        return f"{self.test_id}, Q{self.question_number}"


class Answers(models.Model):
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    is_true = models.BooleanField(default=False)
    match = models.CharField(max_length=50)


class Results(models.Model):
    student_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    points = models.CharField(max_length=20)
    time = models.CharField(max_length=50)


#class Option(models.Model):
#    text = models.CharField(max_length=255)
#    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='options')
#    match = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='matches')

