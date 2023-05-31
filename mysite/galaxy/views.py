import os
import time
import json
from datetime import datetime, timedelta
from itertools import groupby

import requests
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
from django.db.models import Sum, Count
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token, ConfirmMixin, AddTestConstValues


class Index(TemplateView):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tests_to_check = TestsToCheck.objects.filter(is_checked=False)
        context['title'] = 'Main Page'
        context['tests_to_check'] = tests_to_check
        return context


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'galaxy/sign_up.html'
    success_url = reverse_lazy('personal_acc')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign Up'
        return context

    @staticmethod
    def send_email_activation(user, request):
        site = get_current_site(request)
        email_subject = 'Confirm your email'
        email_body = render_to_string('galaxy/email_verify_template.html', {
            'user': user,
            'domain': site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        send_mail(
            email_subject,
            email_body,
            "galaxy.english@yandex.kz",
            [user.email],
            fail_silently=False,
        )

    def form_valid(self, form):
        user = form.save()              # сохраняем форму в бд
        self.send_email_activation(user, self.request)
        return render(self.request, 'galaxy/email_check_page.html')     #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! прямой редирект?????


def email_check_page(request):                  # !!!!!!!!!!!!!!!!!!!!!!!!! буз этой функции?
    return render(request, 'galaxy/email_check_page.html')


def verify_email(request, uid64, token):        # попадаем сюда из письма на почту
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = CustomUser.objects.get(pk=uid)
    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return redirect(reverse_lazy('login'))

    return render(request, 'galaxy/email_verification_failed.html', {'user': user})


def validate_username(request):
    """Check username availability"""
    username = request.GET.get('username', None)
    response = {
        'is_taken': CustomUser.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


def validate_email(request):
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email
    """Check email availability and validate email"""
    email = request.GET.get('email', None)
    try:
        validate_email(email)
        is_valid = True
    except ValidationError:
        is_valid = False

    response = {
        'is_taken': CustomUser.objects.filter(email__iexact=email).exists(),
        'is_valid': is_valid
    }
    return JsonResponse(response)


def validate_password(request):
    """Check if password1 matches password2"""
    password1 = request.GET.get('password1', None)
    password2 = request.GET.get('password2', None)
    response = {
        'matches': password1 == password2
    }
    return JsonResponse(response)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'galaxy/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

    def get_success_url(self):          # при успешном логине перенаправляет
        if not self.request.user.is_email_verified:
            logout(self.request)
            return reverse_lazy('email_check_page')

        #return reverse_lazy('personal_acc', kwargs={'acc_slug': self.request.user.slug})
        return reverse_lazy('home')


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


class ShowGroups(ListView):
    model = Groups
    context_object_name = 'groups'
    template_name = "galaxy/show_groups.html"

    def get_queryset(self):
        return Groups.objects.all()


def add_group(request):
    groupname = request.GET.get('name', None)
    test_type = request.GET.get('test_type', None)
    group = Groups.objects.create(name=groupname, test_type=test_type)
    group.save()
    return redirect('show_groups')


class ShowGroupParticipants(ListView):
    model = CustomUser
    context_object_name = 'participants'
    template_name = "galaxy/show_group_participants.html"

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return CustomUser.objects.filter(group=group_id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        group_obj = Groups.objects.get(id=self.kwargs['group_id'])
        context['title'] = 'Group' + group_obj.name
        context['group'] = group_obj
        return context


def delete_group(request, group_id):
    group = Groups.objects.get(id=group_id)
    group.delete()
    return redirect('show_groups')


def update_student_group(request):
    user = CustomUser.objects.get(id=request.GET.get('student'))
    user.group = Groups.objects.get(id=request.GET.get('group'))
    user.save()
    return JsonResponse({'success': True})


class TestDetails(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('login')
    model = Tests
    template_name = "galaxy/test_details.html"
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


class PassTest(View):
    def get(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)
        user = request.user

        try:
            time_obj = TestTimings.objects.get(test_id=test, user_id=user)
        except Exception as err:
            print(err)  # TestTimings matching query does not exist
            time_obj = TestTimings()
            time_obj.test_id = test
            time_obj.user_id = user
            time_obj.start_time = time.time()
            time_obj.save()

        '''Формируем наполнение страницы'''
        content_dict = {}
        chapters_for_test = Chapters.objects.filter(test_id__id=test.id).order_by('chapter_number')
        for chapter in chapters_for_test:
            questions_for_test = Questions.objects.filter(chapter_id__id=chapter.id).order_by('question_number')
            qa = {}
            for question in questions_for_test:
                if question.question_type == 'match_type':  # Если вопрос на сопоставление
                    qa[question] = {
                        key: Answers.objects.filter(question_id__id=question.id).order_by('answer').values_list(
                            'answer',
                            flat=True)
                        for key in
                        Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').order_by('match')}
                elif question.question_type == 'input_type':  # Вопрос с вводом слова
                    qa[question] = Answers.objects.get(question_id__id=question.id)
                else:  # Вопрос с radio или True/False
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
            content_dict[chapter] = qa

        context = {'test': test,
                   'content_dict': content_dict,
                   'start_time': time_obj.start_time,
                   }

        return render(request, 'galaxy/pass_test.html', context)

    def post(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)
        user = request.user

        '''Подсчитываем время, потраченное на тест и удаляем из сессии время старта'''
        time_obj = TestTimings.objects.get(test_id=test, user_id=user)
        test_time = int(time.time() - time_obj.start_time)
        if test_time > test.time_limit * 60:
            test_time = test.time_limit * 60
        time_obj.delete()

        '''Если ученик не сможет прикрепить ответы или решит не заканчивать экзамен'''
        if 'no_attached_files' in request.session:
            del request.session['no_attached_files']

        if test.part == 'Writing' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')

        if test.part == 'Speaking' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return JsonResponse({'empty_flag': 1})

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
                if question.question_type == 'match_type':  # Подсчёт вопросов на сопоставление
                    question_points = question.points
                    for answer in Answers.objects.filter(question_id__id=question.id).exclude(
                            match__exact=''):  # ??перебираем только "правильные" ответы, отрезая пустышку без match
                        student_answer = request.POST.get(str(answer.id))
                        if student_answer != answer.answer:
                            question_points -= 1
                    if question_points > 0:
                        total_test_points += question_points
                elif question.question_type == 'input_type':  # Подсчет вопросов с вводом
                    answer = Answers.objects.get(question_id__id=question.id)
                    answers = str(answer.answer)
                    right_answers = list(answers.split(','))
                    student_answer = str(request.POST.get(str(answer.id)))
                    if student_answer in right_answers:
                        total_test_points += question.points
                elif question.question_type == 'true_false_type':  # Подсчет вопросов с True/False
                    try:
                        if request.POST.get(str(question.id)) == Questions.objects.get(id=question.id).addition:
                            total_test_points += question.points
                    except:
                        pass
                    pass
                try:  # потому что студент может оставить radio невыбранным
                    obj = Answers.objects.get(pk=request.POST.get(str(question.id)))
                    if obj.is_true:
                        total_test_points += question.points  # Подсчет вопросов с выбором
                except:
                    pass

            else:  # Writing and Speaking
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

        '''Уведомляем учителя о том, что студент выполнил тест, который нуждается в проверке'''
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

        if test.part == 'Writing':
            return HttpResponseRedirect('/test_result_wo_points/')

        if test.part == 'Speaking':
            return JsonResponse({'empty_flag': 0})


        '''Создаем объект результата попытки выполнения теста для 3х категорий'''
        result = Results()
        result.student_id = user
        result.test_id = test
        result.points = total_test_points
        result.time = str(timedelta(seconds=test_time))
        result.save()
        return HttpResponseRedirect('/test_result_with_points/' + str(result.pk) + '/')


class TestResultWOPoints(TemplateView):
    template_name = "galaxy/test_result_wo_points.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wait for results'
        return context


class TestResultWithPoints(DetailView):
    model = Results
    template_name = "galaxy/test_result_with_points.html"
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
    template_name = "galaxy/show_tests.html"
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Available Tests'
        return context

    def get_queryset(self):
        return Tests.objects.all().order_by('type', 'part', 'test_num')


class ShowTestsToCheck(ListView):
    paginate_by = 15
    model = TestsToCheck
    template_name = "galaxy/show_tests_to_check.html"
    context_object_name = 'tests_to_check'

    def get_queryset(self):
        return TestsToCheck.objects.filter(is_checked=False)


class ShowConfirmedStudents(ConfirmMixin, ListView):
    template_name = "galaxy/show_confirmed_students.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirmed Students'
        group_list = Groups.objects.all()
        context['group_list'] = group_list
        return context

    def get_queryset(self):
        return self.foo(True)


class ShowPendingStudents(ConfirmMixin, ListView):
    template_name = "galaxy/show_pending_students.html"

    def get_queryset(self):
        return self.foo(None)


class ShowDeniedStudents(ConfirmMixin, ListView):
    template_name = "galaxy/show_denied_students.html"

    def get_queryset(self):
        return self.foo(False)


def deny_student(request, student_id, template):
    student = CustomUser.objects.get(id=student_id)
    student.is_confirmed = False
    student.group = None
    student.save()
    return redirect(reverse_lazy(template))


def confirm_student(request, student_id, template):
    student = CustomUser.objects.get(id=student_id)
    student.is_confirmed = True
    student.save()
    return redirect(reverse_lazy(template))


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
        context['form'] = TaskCheckForm()       # не нужна?
        test_to_check = context['test_to_check']
        tasks_to_check = TasksToCheck.objects.filter(test_to_check_id=test_to_check)
        context['tasks_to_check'] = tasks_to_check
        return context


#def download(request, document_id):
#    document = get_object_or_404(Document, pk=document_id)
#    response = HttpResponse(document.document, content_type='application/pdf')
#    response['Content-Disposition'] = f'attachment; filename="{document.document.name}"'
#    return response


class AddTestAndChaptersView(AddTestConstValues, View):
    def get(self, request, *args, **kwargs):
        test_form = TestAddForm()
        chapter_formset = formset_factory(ChapterAddForm, extra=0)
        context = {
            'test_form': test_form,
            'chapter_formset': chapter_formset,
        }
        return render(request, 'galaxy/add_test.html', context)

    def post(self, request, *args, **kwargs):
        test_form = TestAddForm(request.POST, request.FILES)
        chapter_formset = formset_factory(ChapterAddForm, extra=0)(request.POST, request.FILES)
        if test_form.is_valid() and chapter_formset.is_valid():
            test_obj = test_form.save(commit=False)
            test_type = test_obj.type
            test_part = test_obj.part
            test_num = Tests.objects.filter(type=test_type, part=test_part).count() + 1
            test_obj.test_num = test_num
            test_obj.save()                                     # Save the Test
            self.add_test_const_values(test_obj)

            for chapter_form in chapter_formset.forms:          # Save the Chapters
                if chapter_form.has_changed():
                    chapter = chapter_form.save(commit=False)
                    chapter.test_id = test_obj
                    chapter.save()

            return redirect('add_q_and_a', test_obj.id)

        context = {
            'test_form': test_form,
            'chapter_formset': chapter_formset,
        }
        return render(request, 'galaxy/add_test.html', context)


class AddQandAView(View):
    def get(self, request, *args, **kwargs):
        test_id = self.kwargs.get('test_id')
        question_form = QuestionAddForm(test_id)
        answer_formset = formset_factory(AnswerAddForm, extra=0)
        sum_of_questions = Questions.objects.filter(test_id=Tests.objects.get(id=test_id)).count()
        context = {
            'question_form': question_form,
            'answer_formset': answer_formset,
            'sum_of_questions': sum_of_questions,
        }

        return render(request, 'galaxy/add_q_and_a.html', context)

    def post(self, request, *args, **kwargs):
        test_id = self.kwargs.get('test_id')

        question_form = QuestionAddForm(test_id, request.POST, request.FILES)
        answer_formset = formset_factory(AnswerAddForm, extra=0)(request.POST, request.FILES)

        if question_form.is_valid() and answer_formset.is_valid():
            question_obj = question_form.save(commit=False)
            question_obj.test_id = Tests.objects.get(id=test_id)
            # Save the question
            question_obj.save()

            # Save the Chapters
            for answer_form in answer_formset.forms:
                if answer_form.has_changed():
                    answer_obj = answer_form.save(commit=False)
                    if question_obj.question_type == 'input_type':
                        answer_obj.answer = answer_obj.answer.upper()

                    answer_obj.question_id = question_obj
                    answer_obj.save()

            return redirect('add_q_and_a', test_id)


class ShowTest(View):
    def get(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)

        content_dict = {}
        chapters_for_test = Chapters.objects.filter(test_id__id=test.id).order_by('chapter_number')
        for chapter in chapters_for_test:
            questions_for_test = Questions.objects.filter(chapter_id__id=chapter.id).order_by('question_number')
            qa = {}
            for question in questions_for_test:
                if question.question_type == 'match_type':
                    qa[question] = {
                        key: Answers.objects.filter(question_id__id=question.id).order_by('answer').values_list(
                            'answer',
                            flat=True)
                        for key in
                        Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').order_by('match')}
                elif question.question_type == 'input_type':
                    qa[question] = Answers.objects.get(question_id__id=question.id)
                else:
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
            content_dict[chapter] = qa

        context = {'test': test,
                   'content_dict': content_dict,
                   }

        return render(request, 'galaxy/show_test.html', context)


def testing_page(request):
    return render(request, 'galaxy/audio_recording_test.html')


class TestingPage(View):
    template_name = 'galaxy/audio_recording_test.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if len(request.FILES) > 0:
            return render(request, 'galaxy/index.html')
        else:
            # Render an error page
            return render(request, 'galaxy/julik.html')


class MakeAnAssessment(TemplateView):
    template_name = 'galaxy/make_an_assessment.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Make an assessment'
        group_list = Groups.objects.all().order_by('name')
        context['group_list'] = group_list
        return context

    def post(self, request, *args, **kwargs):
        group = Groups.objects.get(id=request.POST['group'])
        assessment_date = request.POST['datepicker']
        assessment_date = datetime.strptime(assessment_date, "%m/%d/%Y").date()

        '''Назначение даты 5 рандомным тестам '''
        assessments_by_part = []
        for part in ['Grammar and Vocabulary', 'Listening', 'Reading', 'Speaking', 'Writing']:
            assessments_by_part.append(
                Tests.objects.filter(is_assessment=True, type=group.test_type, part=part).
                exclude(used_in_groups__contains=str(group.id))
                                       )

        for assessment_query in assessments_by_part:
            if len(assessment_query) < 3:
                pass        # notification, that few tests left

            if len(assessment_query) > 0:
                random_assessment = assessment_query.order_by('?')[0]       # rly random or everytime the same?
                assessment = Assessments(test=random_assessment, group=group, date=assessment_date)
                if len(random_assessment.used_in_groups) > 0:
                    random_assessment.used_in_groups += ','
                random_assessment.used_in_groups += str(group.id)
                random_assessment.save()
                assessment.save()
        return redirect('show_current_assessments')


class ShowCurrentAssessments(ListView):
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_current_assessments.html"

    def get_queryset(self):
        #return Tests.objects.exclude(appointed_to_group=None)
        return Assessments.objects.distinct('group', 'date')


def delete_an_assessment(request, assessment_id):
    assessment_object = Assessments.objects.get(id=assessment_id)
    group = assessment_object.group
    date = assessment_object.date
    assessments_to_delete = Assessments.objects.filter(group=group, date=date)
    #print(assessments_to_delete)
    for assessment in assessments_to_delete:
        assessment.delete()

    return redirect('show_current_assessments')
