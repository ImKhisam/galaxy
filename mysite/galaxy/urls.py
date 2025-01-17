from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('debug/', Debug.as_view(), name='debug'),
    path('testing_page', TestingPage.as_view(), name='testing_page'),
    path('black_hole', BlackHole.as_view(), name='black_hole'),

    path('', Index.as_view(), name='home'),
    path('register/', SignUp.as_view(), name='register'),
    path('validate_username', validate_username, name='validate_username'),
    path('validate_email', validate_email, name='validate_email'),
    path('validate_password', validate_password, name='validate_password'),
    path('verify_email/<uid64>/<token>', verify_email, name='verify'),
    path('email_check_page/', email_check_page, name='email_check_page'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="galaxy/password_reset.html"),
         name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="galaxy/password_reset_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="galaxy/password_reset_form.html",
                                                     form_class=NewPassSetForm),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="galaxy/password_reset_done.html"),
         name='password_reset_complete'),

    path('profile/<slug:acc_slug>/', Profile.as_view(), name='profile'),
    path('delete_account/<int:user_id>', delete_account, name='delete_account'),
    path('idioms/', Idioms.as_view(), name='idioms'),
    path('julik/', julik, name='julik'),

    path('groups/', ShowGroups.as_view(), name='show_groups'),
    path('show_group_participants/<int:group_id>/', ShowGroupParticipants.as_view(), name='show_group_participants'),

    path('user_profile/<int:user_pk>/', UserProfile.as_view(), name='user_profile'),
    path('show_user_assessments/<int:user_pk>/', ShowUserAssessments.as_view(), name='show_user_assessments'),
    path('show_user_results/<int:user_pk>/', ShowUserResults.as_view(), name='show_user_results'),

    path('add_group/', add_group, name='add_group'),
    path('update_group_name/', update_group_name, name='update_group_name'),
    path('delete_group/<int:group_id>/', delete_group, name='delete_group'),
    path('ajx_delete_group/', ajx_delete_group, name='ajx_delete_group'),
    path('update_student_group', update_student_group, name='update_student_group'),

    path('my_results/', ShowResults.as_view(), name='show_student_results'),
    path('results/', ShowResultsForTeacher.as_view(), name='show_results'),
    path('filter_results/', filter_results, name='filter_results'),
    path('show_students/', ShowStudents.as_view(), name='show_students'),
    path('filter_students/', filter_students, name='filter_students'),
    path('confirm_deny_student/', confirm_deny_student, name='confirm_deny_student'),
    path('show_tests_to_check/', ShowTestsToCheck.as_view(), name='show_tests_to_check'),
    path('filter_tests_to_check/', filter_tests_to_check, name='filter_tests_to_check'),
    path('checking_test/<int:test_to_check_id>/', CheckingTest.as_view(), name='checking_test'),
    path('rechecking_test/<int:test_to_check_id>/', ReCheckingTest.as_view(), name='rechecking_test'),

    path('test_details/<int:test_pk>/', TestDetails.as_view(), name='test_details'),
    path('pass_test/<int:test_pk>/', PassTest.as_view(), name='pass_test'),
    path('test_result_with_points/<int:res_pk>/', TestResultWithPoints.as_view(), name='test_result_with_points'),
    path('test_result_wo_points/', TestResultWOPoints.as_view(), name='test_result_wo_points'),
    path('result_summary/<int:result_id>/', ResultSummary.as_view(), name='result_summary'),
    path('result_preview/<int:result_id>/', ResultPreview.as_view(), name='result_preview'),
    path('show_colour_result/<int:result_pk>/', ShowColouredResult.as_view(), name='show_colour_result'),

    path('show_tests_and_assessments/', ShowTestsAndAssessments.as_view(), name='show_tests_and_assessments'),
    path('filter_tests_and_assessments', filter_tests_and_assessments, name='filter_tests_and_assessments'),
    path('show_tests_by_part/<type>/', ShowTestsByPart.as_view(), name='show_tests_by_part'),
    path('filter_tests_by_part/', filter_tests_by_part, name='filter_tests_by_part'),
    path('add_test/', AddTestAndChaptersView.as_view(), name='add_test'),
    path('delete_test/', delete_test, name='delete_test'),
    path('add_q_and_a/<int:chapter_id>/', AddQandAView.as_view(), name='add_q_and_a'),
    path('edit_test_data/<int:test_id>/', EditTestData.as_view(), name='edit_test_data'),
    path('edit_chapter_data/<int:chapter_id>/', EditChapterData.as_view(), name='edit_chapter_data'),
    path('delete_chapter/<int:chapter_id>/', delete_chapter, name='delete_chapter'),
    path('edit_q_and_a/<int:question_id>/', EditQandAView.as_view(), name='edit_q_and_a'),
    path('delete_question/<int:question_id>/', delete_question, name='delete_question'),
    path('test/<slug:show_type>/<int:test_pk>/', ShowOrEditTest.as_view(), name='test'),

    path('show_assessments_for_teacher/', ShowAssessmentsForTeacher.as_view(), name='show_assessments_for_teacher'),
    path('filter_assessments_for_teacher/', filter_assessments_for_teacher, name='filter_assessments_for_teacher'),
    path('save_an_assessment/', save_an_assessment, name='save_an_assessment'),
    path('close_assessment/', close_assessment, name='close_assessment'),   # ajax func?
    path('force_open_assessment/', force_open_assessment, name='force_open_assessment'),
    path('deny_assessment/', deny_assessment, name='deny_assessment'),
    path('open_current_assessment/<int:assessment_pk>/', OpenCurrentAssessment.as_view(), name='open_current_assessment'),
    path('show_assessment_results/<int:assessment_pk>/', ShowAssessmentResults.as_view(), name='show_assessment_results'),

    path('show_assessments_for_student/', ShowAssessmentsForStudent.as_view(), name='show_assessments_for_student'),
    path('filter_assessments_for_student/', filter_assessments_for_student, name='filter_assessments_for_student'),
    path('show_assessment_tests/<int:assessment_id>', ShowAssessmentTests.as_view(), name='show_assessment_tests'),

    path('read_and_learn/', ReadAndLearn.as_view(), name='read_and_learn'),
    path('pass_read_and_learn_test/<int:test_pk>/', PassReadAndLearnTest.as_view(), name='pass_read_and_learn_test'),
    ]


