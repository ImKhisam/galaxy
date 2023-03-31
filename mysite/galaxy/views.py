import os
import time
from datetime import datetime, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect
from .forms import *
from django.db.models import Sum


class Index(TemplateView):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Main Page'
        return context


class SignUp(TemplateView):
    template_name = "galaxy/sign_up.html"


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'galaxy/register.html'
    success_url = reverse_lazy('personal_acc')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration'
        return context

    def form_valid(self, form):
        user = form.save()              # сохраняем форму в бд
        login(self.request, user)       # при успешной регистрации сразу логинит
        return redirect('personal_acc', acc_slug=self.request.user.slug)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'galaxy/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

    def get_success_url(self):          # при успешном логине перенаправляет
        return reverse_lazy('personal_acc', kwargs={'acc_slug': self.request.user.slug})


def logout_user(request):
    logout(request)             # станд функция выхода
    return redirect('home')


class PersonalAcc(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "galaxy/personal_acc.html"
    slug_url_kwarg = 'acc_slug'
    # context_object_name = 'acc'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Personal Account'
        return context


class ShowTestStat(ListView):
    model = Results
    template_name = "galaxy/show_test_stat.html"
    context_object_name = 'results'
    extra_context = {'dict': {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
                              for key in Tests.objects.all()}}

    def get_queryset(self):
        return Results.objects.filter(student_id=self.request.user)


class TestPreview(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('login')
    model = Tests
    template_name = "galaxy/test_preview.html"
    pk_url_kwarg = 'test_pk'
    context_object_name = 'test'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Test preview'
        return context


def test(request, test_pk):
    test = get_object_or_404(Tests, id=test_pk)
    if test.start_time == 0:
        test.start_time = time.time()
        test.save()

    content_dict = {}
    chapters_for_test = Chapters.objects.filter(test_id__id=test.id)
    for chapter in chapters_for_test:
        questions_for_test = Questions.objects.filter(chapter_id__id=chapter.id).order_by('question_number')
        qa = {}
        for question in questions_for_test:
            if question.question_type == 'match_type':      # Если вопрос на сопоставление
                qa[question] = {key: Answers.objects.filter(question_id__id=question.id).order_by('answer').values_list('answer', flat=True)
                                for key in Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').order_by('match')}
            elif question.question_type == 'input_type':    # Вопрос с вводом слова
                qa[question] = Answers.objects.get(question_id__id=question.id)
            else:                                       # Вопрос с radio
                qa[question] = Answers.objects.filter(question_id__id=question.id)
        content_dict[chapter] = qa

    if request.method == 'POST':
        '''Подсчитываем время, потраченное на тест и удаляем из сессии время старта'''
        test_time = int(time.time() - test.start_time)
        if test_time > test.time_limit * 60:
            test_time = test.time_limit * 60
        test.start_time = 0
        test.save()
        '''Подсчитываем баллы за тест'''
        total_test_points = 0
        questions_for_test = Questions.objects.filter(test_id__id=test.id).order_by('question_number')
        for question in questions_for_test:
            '''Подсчёт вопросов на сопоставление'''
            if question.question_type == 'match_type':
                question_points = question.points
                for answer in Answers.objects.filter(question_id__id=question.id).exclude(match__exact=''):
                    student_answer = request.POST.get(str(answer.id))
                    if student_answer != answer.answer:
                        question_points -= 1
                if question_points > 0:
                    total_test_points += question_points
            elif question.question_type == 'input_type':
                answer = Answers.objects.get(question_id__id=question.id)
                right_answer = str(answer.answer)
                student_answer = str(request.POST.get(str(answer.id)))
                if student_answer == right_answer:
                    total_test_points += question.points
            '''Подсчёт вопросов с radio'''
            try:        # потому что студент может оставить radio невыбранным
                obj = Answers.objects.get(pk=request.POST.get(str(question.id)))
                if obj.is_true:
                    total_test_points += question.points
            except:
                pass

        student = CustomUser.objects.get(id=request.user.id)
        result = Results()
        result.student_id = student
        result.test_id = test
        result.points = total_test_points
        result.time = str(timedelta(seconds=test_time))
        result.save()
        return HttpResponseRedirect('/test_result/' + str(result.pk) + '/')

    context = {'test': test,
               'content_dict': content_dict,
               'start_time': test.start_time,
               }

    response = render(request, 'galaxy/test.html', context)
    return response


class TestResult(DetailView):
    model = Results
    template_name = "galaxy/test_result.html"
    pk_url_kwarg = 'res_pk'
    context_object_name = 'result'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Test result'
        obj = Results.objects.get(pk=context['result'].pk)
        max_points = Questions.objects.filter(test_id=obj.test_id).aggregate(Sum('points'))['points__sum']
        test_time = obj.time
        context['test_time'] = test_time
        context['max_points'] = max_points
        return context


def showdoc(request, classes_id, doc_type):
    media = settings.MEDIA_ROOT                                     # importing from settings
    obj = get_object_or_404(OlympWay, id=classes_id)                # get path from db
    filepath = os.path.join(media, str(obj.task))                   # uniting path
    if doc_type == 'answer':
        filepath = os.path.join(media, str(obj.answer))
    elif doc_type == 'script':
        filepath = os.path.join(media, str(obj.script))

    try:
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


class Playaudio(DetailView):
    model = OlympWay
    template_name = 'galaxy/play_audio.html'
    pk_url_kwarg = 'classes_id'
    context_object_name = 'file'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '_'.join(('Olymp', context['file'].year, context['file'].classes))
        return context


class Idioms(LoginRequiredMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'idioms'
        return context


def julik(request):
    return render(request, 'galaxy/julik.html')


class ShowTests(ListView):
    model = Tests
    template_name = "galaxy/tests.html"
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] ='tests'
        return context

    #def get_queryset(self):
    #    return Tests.objects.all()
