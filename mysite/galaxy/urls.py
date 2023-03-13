from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('personal_acc/<slug:acc_slug>/', PersonalAcc.as_view(), name='personal_acc'),
    path('oge/', Gse.as_view(), name='oge'),
    path('ege/', Use.as_view(), name='ege'),
    path('dev_skills/', DevSkills.as_view(), name='dev_skills'),
    path('idioms/', Idioms.as_view(), name='idioms'),
    path('julik/', julik, name='julik'),
    path('test/', Test.as_view(), name='test'),
    path('show_doc/<int:classes_id>/<doc_type>/', showdoc, name='show_doc'),
    path('play_audio/<int:classes_id>/', Playaudio.as_view(), name='play_audio'),
    path('listening_test/', ListeningTest.as_view(), name='listening_test')
    ]