from django.shortcuts import render
from django.urls import reverse_lazy


from .forms import *
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView


def teacher_signup_view(request):
    userform = TeacherUserForm()
    teacherform = TeacherForm()
    mydict = {'userForm': userform, 'teacherForm': teacherform}
    if request.method == 'POST':
        userform = TeacherUserForm(request.POST)
        teacherform = TeacherForm(request.POST, request.FILES)
        if userform.is_valid() and teacherform.is_valid():
            user = userform.save()
            user.set_password(user.password)
            user.save()
            teacher = teacherform.save(commit=False)
            teacher.user = user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')

    return render(request, 'users/teachersignup.html', context=mydict)


class LoginTeacher(LoginView):
    form_class = LoginTeacherForm
    template_name = 'users/teacherlogin.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']= 'Login'
        return context

    def get_success_url(self):          # при успешном логине перенаправляет
        return reverse_lazy('personal_acc', kwargs={'acc_slug': self.request.user.slug})
