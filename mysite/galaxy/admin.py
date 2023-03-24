from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea

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
    list_display = ('id', 'test_id', 'points', 'question', 'question_type')


class AnswersAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '60'})},
    }

    list_display = ('id', 'question_id', 'answer', 'is_true')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OlympWay, OlympWayAdmin)
admin.site.register(Tests, TestsAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswersAdmin)