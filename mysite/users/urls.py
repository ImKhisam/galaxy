from django.urls import path
from .views import *


urlpatterns = [
    path('teachersignup', teacher_signup_view,name='teachersignup'),
    path('teacherlogin', LoginTeacher.as_view(),name='teacherlogin'),
    #path('teacherclick', views.teacherclick_view),


    #path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),
    #path('teacher-exam', views.teacher_exam_view,name='teacher-exam'),
    #path('teacher-add-exam', views.teacher_add_exam_view,name='teacher-add-exam'),
    #path('teacher-view-exam', views.teacher_view_exam_view,name='teacher-view-exam'),
    #path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),
#
#
    #path('teacher-question', views.teacher_question_view,name='teacher-question'),
    #path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
    #path('teacher-view-question', views.teacher_view_question_view,name='teacher-view-question'),
    #path('see-question/<int:pk>', views.see_question_view,name='see-question'),
    #path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
    ]