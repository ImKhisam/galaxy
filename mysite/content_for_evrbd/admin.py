from django.contrib import admin
from .models import BrittishBulldog


class BrittishBulldogAdmin(admin.ModelAdmin):
    list_display = ('classes', 'year')


admin.site.register(BrittishBulldog, BrittishBulldogAdmin)
