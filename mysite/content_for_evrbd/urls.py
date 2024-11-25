from django.urls import path

from .views import *

urlpatterns = [
    path('BB/', BB.as_view(), name='BB'),
    path('olymp/', Olymp.as_view(), name='olymp'),
    #path('tnt/', tnt, name='tnt'),
    path('publications/', publications, name='publications'),
    path('master_yls/', master_yls, name='master_yls'),
    path('watch_and_learn/', watch_and_learn, name='watch_and_learn'),
    path('show_doc/<int:classes_id>/<slug:source>/<doc_type>/', showdoc, name='show_doc'),
    path('play_audio/<int:classes_id>/<slug:source>/', Playaudio.as_view(), name='play_audio'),
    path('quiz_preview/', QuizPreview.as_view(), name='quiz_preview'),
    path('show_quiz/<int:quiz_id>/', ShowQuiz.as_view(), name='show_quiz'),

    path('cross_choice', cross_choice, name='cross_choice'),
    path('cross/<cross_num>/', cross, name='cross'),
    ]
