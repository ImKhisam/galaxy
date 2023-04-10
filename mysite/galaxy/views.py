import os
import time
import json
from datetime import datetime, timedelta

from django.db import transaction
from django.forms import formset_factory, modelform_factory

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect, JsonResponse
from .forms import *
from django.db.models import Sum
from django.core.mail import send_mail


class Index(TemplateView):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tests_to_check = TestsToCheck.objects.filter(is_checked=False)
        context['title'] = 'Main Page'
        context['tests_to_check'] = tests_to_check
        return context


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


def validate_username(request):
    """Check username availability"""
    username = request.GET.get('username', None)
    response = {
        'is_taken': CustomUser.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


#class EmailValidationView(View):
#    def post(self, request):
#        data = json.loads(request.body)
#        email = data['email']
#        if CustomUser.objects.filter(email__iexact=email).exists():
#            return JsonResponse({'email_error': 'sorry email is already taken'})
#        return JsonResponse({'username_valid': True})


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


class ShowResults(ListView):
    paginate_by = 15
    model = Results
    template_name = "galaxy/show_results.html"
    context_object_name = 'results'
    #extra_context = {'dict': {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
    #                          for key in Tests.objects.all()}}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My results'
        context['dict'] = {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
                           for key in Tests.objects.all()}
        return context

    def get_queryset(self):
        return Results.objects.filter(student_id=self.request.user)



class ResultPreview(DetailView):
    model = Results
    template_name = 'galaxy/result_preview.html'
    pk_url_kwarg = 'result_pk'
    context_object_name = 'result'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Result commentary'
        return context


class TestPreview(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('login')
    model = Tests
    template_name = "galaxy/test_preview.html"
    pk_url_kwarg = 'test_pk'
    context_object_name = 'test'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        test = context['test']
        user = self.request.user
        try:
            unfinished_try = TestTimings.objects.get(test_id=test, user_id=user)
            unfinished_try = 1
        except:
            unfinished_try = 0

        context['title'] = 'Test preview'
        context['unfinished_try'] = unfinished_try
        return context


def test(request, test_pk):
    test = get_object_or_404(Tests, id=test_pk)
    user = request.user
    try:
        time_obj = TestTimings.objects.get(test_id=test, user_id=user)
    except:
        time_obj = TestTimings()
        time_obj.test_id = test
        time_obj.user_id = user
        time_obj.start_time = time.time()
        time_obj.save()
    start_time = time_obj.start_time
    '''Формируем наполнение страницы'''
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
            else:                                       # Вопрос с radio или True/False
                qa[question] = Answers.objects.filter(question_id__id=question.id)
        content_dict[chapter] = qa

    if request.method == 'POST':
        #student = CustomUser.objects.get(id=request.user.id)
        '''Подсчитываем время, потраченное на тест и удаляем из сессии время старта'''
        test_time = int(time.time() - start_time)
        if test_time > test.time_limit * 60:
            test_time = test.time_limit * 60
        time_obj.delete()

        '''Если ученик не сможет прикрепить ответы или решит не заканчивать экзамен'''
        if 'no_attached_files' in request.session:
            del request.session['no_attached_files']
        if len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')

        '''Создаем объект теста для проверки'''
        if test.part in ['Writing', 'Speaking']:
            test_to_check = TestsToCheck()
            test_to_check.test_id = test
            test_to_check.student_id = user
            test_to_check.save()

        '''Подсчитываем баллы за тест для 3х категорий'''
        total_test_points = 0
        questions_for_test = Questions.objects.filter(test_id__id=test.id).order_by('question_number')
        for question in questions_for_test:
            if test.part not in ['Writing', 'Speaking']:
                if question.question_type == 'match_type':          # Подсчёт вопросов на сопоставление
                    question_points = question.points
                    for answer in Answers.objects.filter(question_id__id=question.id).exclude(match__exact=''):
                        student_answer = request.POST.get(str(answer.id))
                        if student_answer != answer.answer:
                            question_points -= 1
                    if question_points > 0:
                        total_test_points += question_points
                elif question.question_type == 'input_type':        # Подсчет вопросов с вводом
                    answer = Answers.objects.get(question_id__id=question.id)
                    answers = str(answer.answer)
                    print(answers)
                    right_answers = list(answers.split(','))
                    print(right_answers)
                    student_answer = str(request.POST.get(str(answer.id)))
                    if student_answer in right_answers:
                        total_test_points += question.points
                elif question.question_type == 'true_false_type':   # Подсчет вопросов с True/False
                    try:
                        if request.POST.get(str(question.id)) == Questions.objects.get(id=question.id).addition:
                            total_test_points += question.points
                    except:
                        pass
                    pass
                try:        # потому что студент может оставить radio невыбранным
                    obj = Answers.objects.get(pk=request.POST.get(str(question.id)))
                    if obj.is_true:
                        total_test_points += question.points        # Подсчет вопросов с выбором
                except:
                    pass
            else:       # Writing and Speaking
                '''Создаем объект задания для проверки'''
                task_to_check = TasksToCheck()
                try:
                    media1_index = str(question.id) + '_media1'
                    media1 = request.FILES[media1_index]
                    task_to_check.media1 = media1
                except:
                    pass
                try:
                    media2_index = str(question.id) + '_media2'
                    media2 = request.FILES[media2_index]
                    task_to_check.media2 = media2
                except:
                    pass
                task_to_check.test_to_check_id = test_to_check
                task_to_check.question_id = question
                task_to_check.save()

        if test.part in ['Writing', 'Speaking']:
            stdnt = test_to_check.student_id.first_name + ' ' + test_to_check.student_id.last_name
            message = stdnt + ' passed test that you need to check '
            send_mail(
                "New Test to check",
                message,
                "galaxy.english@yandex.kz",
                ["caramellapes@yandex.ru"],
                fail_silently=False,
            )

            return HttpResponseRedirect('/test_result_wo_points/')

        '''Создаем объект результата попытки выполнения теста'''
        result = Results()
        result.student_id = user
        result.test_id = test
        result.points = total_test_points
        result.time = str(timedelta(seconds=test_time))
        result.save()
        return HttpResponseRedirect('/test_result_with_points/' + str(result.pk) + '/')

    context = {'test': test,
               'content_dict': content_dict,
               'start_time': start_time,
               }

    response = render(request, 'galaxy/test.html', context)
    return response


class TestResultWOPoints(TemplateView):
    template_name = "galaxy/test_result_wo_points.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wait for results'
        return context


class TestResultWithPoints(DetailView):
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


class ShowTestsToCheck(ListView):
    model = TestsToCheck
    template_name = "galaxy/tests_to_check.html"
    context_object_name = 'tests_to_check'

    def get_queryset(self):
        return TestsToCheck.objects.filter(is_checked=False)


class CheckingTest(DetailView):
    model = TestsToCheck
    template_name = 'galaxy/checking_test.html'
    pk_url_kwarg = 'test_to_check_id'
    context_object_name = 'test_to_check'

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('test_to_check_id')
        test_to_check = TestsToCheck.objects.get(id=pk)
        tasks_to_check = TasksToCheck.objects.filter(test_to_check_id=test_to_check)
        sum_points_for_test = 0
        for task in tasks_to_check:
            index = str(task.id)
            task.points = request.POST.get(index)
            sum_points_for_test += int(request.POST.get(index))
            task.save()
        test_to_check.is_checked = True
        test_to_check.save()

        '''Создание результата для отображения у ученика'''
        result = Results()
        result.student_id = test_to_check.student_id
        result.test_id = test_to_check.test_id
        result.points = sum_points_for_test
        result.commentary = request.POST.get('commentary')
        result.save()

        return redirect('show_tests_to_check')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'checking test'
        context['form'] = TaskCheckForm()
        test_to_check = context['test_to_check']
        tasks_to_check = TasksToCheck.objects.filter(test_to_check_id=test_to_check)
        context['tasks_to_check'] = tasks_to_check
        return context


#def download(request, document_id):
#    document = get_object_or_404(Document, pk=document_id)
#    response = HttpResponse(document.document, content_type='application/pdf')
#    response['Content-Disposition'] = f'attachment; filename="{document.document.name}"'
#    return response


#class AddTest(View):
#    def get(self, request, *args, **kwargs):
#        test_form = TestAddForm()
#        chapter_forms = [ChapterAddForm(prefix=str(i)) for i in range(2)]
#        return render(request, 'galaxy/add_test.html', {'test_form': test_form, 'chapter_forms': chapter_forms})
#
#    def post(self, request, *args, **kwargs):
#        test_form = TestAddForm(request.POST)
#        chapter_forms = [ChapterAddForm(request.POST, prefix=str(i)) for i in range(2)]
#        if test_form.is_valid() and all([form.is_valid() for form in chapter_forms]):
#            testing = test_form.save(commit=False)
#            test_type = testing.type
#            test_num = Tests.objects.filter(type=test_type).count() + 1
#            testing.test_num = test_num
#            testing.save()
#            for form in chapter_forms:
#                chapter = form.save(commit=False)
#                chapter.test_id = testing
#                chapter.save()
#            return redirect('tests')
#        else:
#            return render(request, 'galaxy/add_test.html', {'test_form': test_form, 'chapter_forms': chapter_forms})


def add_test_and_chapters(request):
    test_form = TestAddForm()
    chapter_formset = formset_factory(ChapterAddForm, extra=0)

    if request.method == 'POST':
        test_form = TestAddForm(request.POST, request.FILES)
        chapter_formset = chapter_formset(request.POST, request.FILES)

        if test_form.is_valid() and chapter_formset.is_valid():
            testing = test_form.save(commit=False)
            test_type = testing.type
            test_part = testing.part
            test_num = Tests.objects.filter(type=test_type, part=test_part).count() + 1
            testing.test_num = test_num
            # Save the Test
            testing.save()
            # Save the Chapters

            for chapter_form in chapter_formset.forms:
                if chapter_form.has_changed():
                    chapter = chapter_form.save(commit=False)
                    chapter.test_id = testing
                    chapter.save()

            return redirect('add_q_and_a', chapter.id)

    context = {
        'test_form': test_form,
        'chapter_formset': chapter_formset,
    }

    return render(request, 'galaxy/add_test.html', context)


#def sof(request, test_id):
#    chapter = Chapters()
#    if request.method == 'POST':
#        survey_form = ChapterForm(request.POST, instance=chapter)
#        question_formset = QuestionFormset(
#            request.POST, prefix='questions', instance=chapter)
#
#        if survey_form.is_valid() and question_formset.is_valid():
#            survey_form.save()
#            question_formset.save()
#            # url = '/preview/{}'.format(survey.pk)
#            # return HttpResponseRedirect(url)
#    else:
#        survey_form = ChapterForm(instance=chapter)
#        question_formset = QuestionFormset(instance=chapter, prefix='questions')
#
#    context = {
#        'survey_form': survey_form,
#        'question_formset': question_formset,
#    }
#
#    return render(request, 'galaxy/sof.html', context)


#class QuestionsAndAnswersView(FormView):
#    template_name = 'galaxy/add_question_test.html'
#    form_class = QuestionFormSet
#    success_url = reverse_lazy('success')
#
#    def get_context_data(self, **kwargs):
#        data = super(QuestionsAndAnswersView, self).get_context_data(**kwargs)
#        if self.request.POST:
#            data['question_formset'] = QuestionFormSet(self.request.POST, prefix='question')
#            data['answer_formset'] = AnswerFormSet(self.request.POST, prefix='answer')
#        else:
#            data['question_formset'] = QuestionFormSet(prefix='question')
#            data['answer_formset'] = AnswerFormSet(prefix='answer')
#        return data
#
#    def form_valid(self, form):
#        context = self.get_context_data()
#        question_formset = context['question_formset']
#        answer_formset = context['answer_formset']
#        if question_formset.is_valid() and answer_formset.is_valid():
#            self.object = form.save()
#            question_formset.instance = self.object
#            question_formset.save()
#            answer_formset.instance = self.object
#            answer_formset.save()
#            return HttpResponseRedirect(self.get_success_url())
#        else:
#            return self.render_to_response(self.get_context_data(form=form))


def add_questions_to_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapters, id=chapter_id)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_formset = AnswerFormSet(request.POST)

        if question_form.is_valid() and answer_formset.is_valid():
            question = question_form.save(commit=False)
            question.chapter = chapter
            question.save()

            answers = answer_formset.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save()

            return redirect('chapter_detail', chapter_id=chapter.id)

    else:
        question_form = QuestionForm()
        answer_formset = AnswerFormSet()

    context = {
        'chapter': chapter,
        'question_form': question_form,
        'answer_formset': answer_formset,
    }
    return render(request, 'galaxy/add_questions_to_chapter.html', context)
