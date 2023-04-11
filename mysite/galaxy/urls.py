from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'), # old sign up
    path('validate_username', validate_username, name='validate_username'),
    path('email_validation', email_validation, name='email_validation'),
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
    path('test_result_with_points/<int:res_pk>/', TestResultWithPoints.as_view(), name='test_result_with_points'),
    path('test_result_wo_points/', TestResultWOPoints.as_view(), name='test_result_wo_points'),
    path('show_results', ShowResults.as_view(), name='show_results'),
    path('result_preview/<int:result_pk>', ResultPreview.as_view(), name='result_preview'),

    path('tests/', ShowTests.as_view(), name='tests'),
    path('add_test/', add_test_and_chapters, name='add_test'),
    #path('add_q_and_a/<int:test_id>', add_questions_and_answers, name='add_q_and_a'),
    path('add_q_and_a/<int:chapter_id>', add_questions_to_chapter, name='add_q_and_a'),
    path('show_tests_to_check/', ShowTestsToCheck.as_view(), name='show_tests_to_check'),
    path('checking_test/<int:test_to_check_id>', CheckingTest.as_view(), name='checking_test'),
    ]