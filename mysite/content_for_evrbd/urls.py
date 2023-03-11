from django.urls import path

from .views import *

urlpatterns = [
    path('play_video/', play_video, name='play_video'),
    path('cross/<cross_num>/', cross, name='cross'),
    path('show_doc/<int:classes_id>/', ShowDoc, name='show_doc'),
    path('play_audio/<int:classes_id>/', Playaudio.as_view(), name='play_audio')
    ]