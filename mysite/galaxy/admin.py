from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterUserForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = RegisterUserForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'first_name', 'last_name', 'role', 'email', 'is_confirmed')
    list_editable = ('is_confirmed',)


class OlympWayAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'stage', 'classes', 'task', 'answer', 'audio', 'script')


class TestsAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'part', 'test_num')


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'points', 'question')


class AnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'is_true')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OlympWay, OlympWayAdmin)
admin.site.register(Tests, TestsAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswersAdmin)