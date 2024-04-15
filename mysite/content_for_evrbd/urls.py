from django.urls import path

from .views import *

urlpatterns = [
    path('BB/', BB.as_view(), name='BB'),
    path('olymp/', Olymp.as_view(), name='olymp'),
    path('play_video/', play_video, name='play_video'),
    path('show_doc/<int:classes_id>/', showdoc, name='show_doc'),
    path('play_audio/<int:classes_id>/', Playaudio.as_view(), name='play_audio'),
    path('quiz_preview/', QuizPreview.as_view(), name='quiz_preview'),
    path('show_quiz/<int:quiz_id>/', ShowQuiz.as_view(), name='show_quiz'),

    path('cross_choice', cross_choice, name='cross_choice'),
    path('cross/<cross_num>/', cross, name='cross'),
    ]
