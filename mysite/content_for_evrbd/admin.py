from django.contrib import admin
from .models import *


class BritishBulldogAdmin(admin.ModelAdmin):
    list_display = ('year', 'classes', 'content', 'audio')


class OlympWayAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'stage', 'classes', 'task', 'answer', 'audio', 'script')


class QuizzesAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz', 'answer')


admin.site.register(Video)
admin.site.register(BritishBulldog, BritishBulldogAdmin)
admin.site.register(OlympWay, OlympWayAdmin)
admin.site.register(Quizzes, QuizzesAdmin)
