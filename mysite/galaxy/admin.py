from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea

from .forms import SignUpForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'first_name', 'last_name', 'role', 'email', 'is_confirmed')
    list_editable = ('is_confirmed',)


class GroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'test_type')


class TestsAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'part', 'test_num', 'time_limit')


class ReadAndLearnTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_num', 'type')


class ChaptersAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_id', 'read_and_learn_test', 'chapter_number', 'text')


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_id', 'chapter_id', 'question_number', 'points', 'question', 'question_type')


class AnswersAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '60'})},
    }

    list_display = ('id', 'question_id', 'answer', 'match', 'is_true')


class ResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'test_id', 'date', 'points', 'time', 'media')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Groups, GroupsAdmin)
admin.site.register(Tests, TestsAdmin)
admin.site.register(ReadAndLearnTest, ReadAndLearnTestAdmin)
admin.site.register(Chapters, ChaptersAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswersAdmin)
admin.site.register(Results, ResultsAdmin)
