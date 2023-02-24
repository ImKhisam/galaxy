from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterUserForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = RegisterUserForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'is_confirmed']
    list_editable = ('is_confirmed',)
    #prepopulated_fields = {"slug": ("username")}


admin.site.register(CustomUser, CustomUserAdmin)
