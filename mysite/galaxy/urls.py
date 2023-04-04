from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'), # old sign up
    path('validate_username', validate_username, name='validate_username'),
    #path('validate_email', EmailValidationView.as_view(), name='validate_email'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('personal_acc/<slug:acc_slug>/', PersonalAcc.as_view(), name='personal_acc'),
    path('idioms/', Idioms.as_view(), name='idioms'),
    path('julik/', julik, name='julik'),
    path('show_doc/<int:classes_id>/<doc_type>/', showdoc, name='show_doc'),
    path('play_audio/<int:classes_id>/', Playaudio.as_view(), name='play_audio'),
    #path('listening_test/', ListeningTest.as_view(), name='listening_test'),


    path('test_preview/<int:test_pk>/', TestPreview.as_view(), name='test_preview'),
    path('test/<int:test_pk>/', test, name='test'),
    path('test_result/<int:res_pk>/', TestResult.as_view(), name='test_result'),
    path('show_test_stat', ShowTestStat.as_view(), name='show_test_stat'),

    path('tests/', ShowTests.as_view(), name='tests'),
    path('add_test/', add_test_and_chapters, name='add_test'),
    ]