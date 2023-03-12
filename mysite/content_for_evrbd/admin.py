from django.contrib import admin
from .models import *


class BritishBulldogAdmin(admin.ModelAdmin):
    list_display = ('year', 'classes', 'content', 'audio')


class QuizzesAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz', 'answer')


admin.site.register(Video)
admin.site.register(BritishBulldog, BritishBulldogAdmin)
admin.site.register(Quizzes, QuizzesAdmin)
