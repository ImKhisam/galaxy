from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('personal_acc/', Personal_Acc.as_view(), name='personal_acc'),
    path('oge/', Oge.as_view(), name='oge'),
    path('ege/', Ege.as_view(), name='ege'),
    path('dev_skills/', Dev_skills.as_view(), name='dev_skills'),
    path('olymp/', Olymp.as_view(), name='olymp'),
    path('BB/', BB.as_view(), name='BB'),
    path('idioms/', Idioms.as_view(), name='idioms'),
    path('fun_room/', Fun_room.as_view(), name='fun_room'),
    path('julik/', julik, name='julik'),
    ]