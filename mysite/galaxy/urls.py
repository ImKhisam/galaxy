from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('register/', SignUp.as_view(), name='register'),
    path('validate_username', validate_username, name='validate_username'),
    path('validate_email', validate_email, name='validate_email'),
    path('validate_password', validate_password, name='validate_password'),
    path('verify_email/<uid64>/<token>', verify_email, name='verify'),
    path('email_check_page/', email_check_page, name='email_check_page'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('personal_acc/<slug:acc_slug>/', PersonalAcc.as_view(), name='personal_acc'),
    path('idioms/', Idioms.as_view(), name='idioms'),
    path('julik/', julik, name='julik'),
    path('show_doc/<int:classes_id>/<doc_type>/', showdoc, name='show_doc'),
    path('play_audio/<int:classes_id>/', Playaudio.as_view(), name='play_audio'),

    path('groups/', ShowGroups.as_view(), name='show_groups'),
    path('show_group_participants/<int:group_id>/', ShowGroupParticipants.as_view(), name='show_group_participants'),
    path('add_group/', add_group, name='add_group'),
    path('delete_group/<int:group_id>/', delete_group, name='delete_group'),
    path('update_student_group', update_student_group, name='update_student_group'),

    path('results/', ShowResults.as_view(), name='show_results'),
    path('show_confirmed_students/', ShowConfirmedStudents.as_view(), name='show_confirmed_students'),
    path('show_pending_students/', ShowPendingStudents.as_view(), name='show_pending_students'),
    path('show_denied_students/', ShowDeniedStudents.as_view(), name='show_denied_students'),
    path('deny_student/<int:student_id>/<template>', deny_student, name='deny_student'),
    path('confirm_student/<int:student_id>/<template>', confirm_student, name='confirm_student'),
    path('show_tests_to_check/', ShowTestsToCheck.as_view(), name='show_tests_to_check'),
    path('checking_test/<int:test_to_check_id>', CheckingTest.as_view(), name='checking_test'),


    path('test_details/<int:test_pk>/', TestDetails.as_view(), name='test_details'),
    path('pass_test/<int:test_pk>/', PassTest.as_view(), name='pass_test'),
    path('test_result_with_points/<int:res_pk>/', TestResultWithPoints.as_view(), name='test_result_with_points'),
    path('test_result_wo_points/', TestResultWOPoints.as_view(), name='test_result_wo_points'),
    path('result_preview/<int:result_pk>', ResultPreview.as_view(), name='result_preview'),

    path('show_tests/', ShowTests.as_view(), name='show_tests'),
    path('add_test/', AddTestAndChaptersView.as_view(), name='add_test'),
    path('add_q_and_a/<int:test_id>/', AddQandAView.as_view(), name='add_q_and_a'),
    #path('add_q_and_a/<int:chapter_id>', add_questions_to_chapter, name='add_q_and_a'),

    path('make_an_assessment/', MakeAnAssessment.as_view(), name='make_an_assessment'),
    path('show_current_assessments/', ShowCurrentAssessments.as_view(), name='show_current_assessments'),

    path('testing_page', TestingPage.as_view(), name='testing_page'),
    ]