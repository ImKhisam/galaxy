from django.contrib import admin
from .models import *


class BritishBulldogAdmin(admin.ModelAdmin):
    list_display = ('year', 'classes', 'content', 'audio')


admin.site.register(Video)
admin.site.register(BritishBulldog, BritishBulldogAdmin)