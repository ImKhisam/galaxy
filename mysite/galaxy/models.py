from autoslug import AutoSlugField
from django import forms
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse


class Groups(models.Model):
    GSE = 'GSE'
    USE = 'USE'
    choices_in_type = [
        (GSE, 'GSE'),
        (USE, 'USE'),
    ]

    name = models.CharField(max_length=20)
    test_type = models.CharField(max_length=255, verbose_name='Type of exam', choices=choices_in_type)
    #has_assessment = models.BooleanField(default=False)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    role_choice = ((None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher'))
    role = models.CharField(max_length=100, choices=role_choice)
    is_confirmed = models.BooleanField()
    slug = AutoSlugField(populate_from='username')
    group = models.ForeignKey(Groups, null=True, on_delete=models.SET_NULL)
    assessments_passed = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('personal_acc', kwargs={'acc_slug': self.slug})


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

    def __str__(self):
        return f"{self.year}, {self.stage}, {self.classes}"

    class Meta:
        ordering = ['year', 'stage']


def content_file_name_test(instance, filename):
    return '/'.join(['test', instance.type, instance.part, str(instance.test_num), filename])


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
    test_num = models.PositiveIntegerField()
    type = models.CharField(max_length=255, verbose_name='Type of exam', choices=choices_in_type)
    part = models.CharField(max_length=255, verbose_name='Part of exam', choices=choices_in_part)
    test_details = models.TextField(default="Текст, который выводится перед началом теста")
    time_limit = models.PositiveIntegerField()
    media = models.FileField(upload_to=content_file_name_test, blank=True)
    is_assessment = models.BooleanField(default=False)           # Разделение тестов на проверочные работы и свободную практику
    groups = models.ManyToManyField(Groups, through="Assessments")
    used_in_groups = models.CharField(max_length=200, blank=True)        # Группы, которым уже назначался тест

    def __str__(self):
        return f"{self.type}, {self.part}, Test №{self.test_num}"

    class Meta:
        ordering = ['type', 'part']


class Assessments(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)  # Дата сдачи теста
    is_passed = models.BooleanField(default=False)


class TestTimings(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    start_time = models.FloatField(default=0)


def content_file_name_chapter(instance, filename):
    return '/'.join(['test', instance.test_id.type, instance.test_id.part, \
                     str(instance.test_id.test_num), "Chapter" + str(instance.chapter_number), filename])


class Chapters(models.Model):
    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    chapter_number = models.PositiveIntegerField()
    info = models.TextField(blank=True)
    text_name = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True)
    media = models.FileField(upload_to=content_file_name_chapter, blank=True)

    def __str__(self):
        return f"{self.test_id}, Chapter #{self.chapter_number}"


class Questions(models.Model):
    single_choice_type = 'single_choice_type'
    match_type = 'match_type'
    input_type = 'input_type'
    true_false_type = 'true_false_type'
    file_adding_type = 'file_adding_type'
    choices_in_question_type = [
        (single_choice_type, 'single_choice_type'),
        (match_type, 'match_type'),
        (input_type, 'input_type'),
        (true_false_type, 'true_false_type'),
        (file_adding_type, 'file_adding_type')
    ]

    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    chapter_id = models.ForeignKey(Chapters, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    question = models.TextField()
    addition_before = models.CharField(max_length=50, blank=True)
    addition_after = models.CharField(max_length=50, blank=True)
    question_number = models.PositiveIntegerField()
    question_type = models.CharField(max_length=255, verbose_name='Type of question', choices=choices_in_question_type)
    time_limit = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return f"{self.test_id}, {self.chapter_id}, Q{self.question_number}"


class Answers(models.Model):
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    is_true = models.BooleanField(default=False)
    addition = models.TextField(default='None')
    match = models.CharField(max_length=50, blank=True)


class Results(models.Model):
    student_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    points = models.CharField(max_length=20)
    detailed_points = models.CharField(max_length=200, blank=True)
    record_answers = models.TextField(max_length=600, blank=True)
    time = models.CharField(max_length=50, blank=True)
    commentary = models.TextField(max_length=600, blank=True)


class TestsToCheck(models.Model):
    test_id = models.ForeignKey(Tests, on_delete=models.CASCADE)
    student_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    #date = models.DateTimeField(auto_now=True)
    is_checked = models.BooleanField(default=False)


def content_file_name_check(instance, filename):
    return '/'.join(['test', 'TestsToCheck', str(instance.question_id), filename])


class TasksToCheck(models.Model):
    test_to_check_id = models.ForeignKey(TestsToCheck, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
    media1 = models.FileField(upload_to=content_file_name_check, blank=True)
    media2 = models.FileField(upload_to=content_file_name_check, blank=True)
    points = models.CharField(max_length=20, default=0)
