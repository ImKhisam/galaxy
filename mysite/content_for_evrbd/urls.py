from django.urls import path

from .views import *

urlpatterns = [
    #path('BB/', BB_years.as_view(), name='BB'),
    #path('show_bb/<slug:bb_slug>/', BB_year.as_view(), name='show_bb_year'),
    path('show_doc/<int:classes_id>/', pdf_view, name='show_doc'),
    path('play_audio/<int:classes_id>/', Play_audio.as_view(), name='play_audio')
    ]