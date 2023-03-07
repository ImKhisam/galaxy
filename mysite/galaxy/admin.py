from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterUserForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = RegisterUserForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'is_confirmed')
    list_editable = ('is_confirmed',)


class BritishBulldogAdmin(admin.ModelAdmin):
    list_display = ('classes', 'year')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BritishBulldog, BritishBulldogAdmin)