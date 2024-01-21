import os
import time
import json
from datetime import datetime, timedelta, date
from itertools import groupby
from mutagen.mp3 import MP3
import requests
from django.forms import formset_factory, modelform_factory

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect, JsonResponse
from .forms import *
from django.db.models import Sum, Count, Q
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token, NotLoggedIn, ConfirmMixin, AddTestConstValues, TeacherUserMixin, \
    ConfirmStudentMixin, teacher_check, ChooseAddQuestForm, AddQuestionConstValues, AddChapterConstValues
from django.contrib.auth.views import PasswordResetView
from pydub import AudioSegment
import base64


class Index(TemplateView, LoginRequiredMixin):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tests_to_check = TestsToCheck.objects.filter(is_checked=False)
        context['title'] = 'Main Page'
        context['tests_to_check'] = tests_to_check
        return context


class SignUp(NotLoggedIn, CreateView):
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


def email_check_page(request):                  # !!!!!!!!!!!!!!!!!!!!!!!!! без этой функции?
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


class LoginUser(NotLoggedIn, LoginView):
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


class ResetPassView(PasswordResetView):
    template_name = 'galaxy/password_reset.html'
    email_template_name = 'galaxy/password_reset_email.html'
    #subject_template_name = 'password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')


class PersonalAcc(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = CustomUser
    template_name = "galaxy/personal_acc.html"
    slug_url_kwarg = 'acc_slug'
    # context_object_name = 'acc'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Personal Account'
        return context


def delete_account(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()
    logout(request)
    return redirect('home')



class ShowResults(LoginRequiredMixin, ConfirmStudentMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 15
    model = Results
    template_name = "galaxy/show_results.html"
    context_object_name = 'results'
    #extra_context = {'dict': {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
    #                          for key in Tests.objects.all()}}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My results'
        context['pagination_number'] = self.paginate_by
        context['dict'] = {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
                           for key in Tests.objects.all()}
        return context

    def get_queryset(self):
        return Results.objects.filter(student_id=self.request.user)


class ResultPreview(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Results
    template_name = 'galaxy/result_preview.html'
    pk_url_kwarg = 'result_pk'
    context_object_name = 'result'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Result commentary'
        return context


class ShowGroups(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Groups
    context_object_name = 'groups'
    template_name = "galaxy/show_groups.html"

    def get_queryset(self):
        return Groups.objects.all()


#@user_passes_test(teacher_check)
def add_group(request):
    group_name = request.GET.get('name', None)
    test_type = request.GET.get('test_type', None)
    group = Groups.objects.create(name=group_name, test_type=test_type)
    group.save()
    return redirect('show_groups')


@user_passes_test(teacher_check, login_url='home')
def update_group_name(request):
    group_id = request.GET.get('group_id', None)
    new_name = request.GET.get('new_name', None)
    try:
        group_obj = Groups.objects.get(pk=group_id)
        old_name = group_obj.name
        group_obj.name = new_name
        group_obj.save()
        '''change group name in assessment tests'''
        tests_objects = Tests.objects.filter(used_in_groups__contains=old_name)
        for test in tests_objects:
            groups_list = test.used_in_groups.split(', ')
            groups_list.remove(old_name)
            groups_list.append(new_name)
            test.used_in_groups = ', '.join(groups_list)
            test.save()
        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False, 'error': 'Error'})


class ShowGroupParticipants(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
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


@user_passes_test(teacher_check, login_url='home')
def delete_group(request, group_id):
    group = Groups.objects.get(id=group_id)
    name_to_delete = group.name
    group.delete()
    tests_with_group_in_list = Tests.objects.filter(used_in_groups__contains=name_to_delete)
    for test in tests_with_group_in_list:
        groups_list = test.used_in_groups.split(', ')
        groups_list.remove(name_to_delete)
        test.used_in_groups = ', '.join(groups_list)
        test.save()
    return redirect('show_groups')


@user_passes_test(teacher_check, login_url='home')
def update_student_group(request):
    user = CustomUser.objects.get(id=request.GET.get('student'))
    user.group = Groups.objects.get(id=request.GET.get('group'))
    user.save()
    return JsonResponse({'success': True})


class TestDetails(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    #login_url = reverse_lazy('login')
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


class PassTest(LoginRequiredMixin, ConfirmStudentMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)
        user = request.user
        template = 'galaxy/pass_speaking_test.html' if test.part == 'Speaking' else 'galaxy/pass_test.html'

        if str(test.id) in user.assessments_passed:
            return render(request, 'galaxy/julik.html')

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
                #audio_media_fl = 0
                #if test.part == 'Speaking' and str(question.media)[-3:] in ['wav', 'mp3', 'aac']:
                #    audio_media_fl = 1
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

        return render(request, template, context)

    def add_detail_points(self, question, detailed_test_points, points):
        if len(detailed_test_points) > 0:
            detailed_test_points += ', '
        detailed_test_points += (str(question.question_number) + ') ' + str(points) + '/' + str(question.points))
        return detailed_test_points

    @staticmethod
    def add_answer_to_record(record_to_add_in, answer_to_add, separation_item):
        if len(record_to_add_in) > 0:
            record_to_add_in += separation_item
        if answer_to_add == 'Выберите ответ':
            answer_to_add = 'No answer'
        record_to_add_in += answer_to_add
        return record_to_add_in

    #@staticmethod
    #def convert_to_mp3(file_path):
    #    print('IM IN COVERT')
    #    import subprocess
    #    mp3_file_path = file_path.replace('.wav', '.mp3')
    #    # Use FFmpeg to convert the WAV file to MP3
    #    subprocess.run(["ffmpeg", "-i", file_path, mp3_file_path])
    #    print('IM OUT CONVERT')
    #    return mp3_file_path

    #@staticmethod
    #def convert_wav_to_mp3(wav_path, mp3_path):
    #    sound = AudioSegment.from_wav(wav_path)
    #    sound.export(mp3_path, format="mp3")

    def post(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)
        user = request.user
        
        '''Подсчитываем время, потраченное на тест и удаляем из сессии время старта'''
        time_obj = TestTimings.objects.get(test_id=test, user_id=user)
        test_time = int(time.time() - time_obj.start_time)  # in seconds?
        if test_time > test.time_limit:
            test_time = test.time_limit
        time_obj.delete()

        '''Если ученик не сможет прикрепить ответы или решит не заканчивать экзамен'''
        if 'no_attached_files' in request.session:      # if it remained from previous test
            del request.session['no_attached_files']

        if test.part == 'Writing' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')

        if test.part == 'Speaking' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')
            #return JsonResponse({'empty_flag': 1})

        '''Создаем объект теста для проверки'''
        if test.part in ['Writing', 'Speaking']:
            test_to_check = TestsToCheck()
            test_to_check.test_id = test
            test_to_check.student_id = user
            test_to_check.save()

        if test.is_assessment:
            if len(user.assessments_passed) > 0:
                user.assessments_passed += ','
            user.assessments_passed += str(test.id)
            user.save()

        '''Подсчитываем баллы за тест для 3х категорий'''
        total_test_points = 0
        detailed_test_points = ''
        record_test_answers = ''
        questions_for_test = Questions.objects.filter(test_id__id=test.id).order_by('question_number')
        for question in questions_for_test:
            if test.part not in ['Writing', 'Speaking']:
                if question.question_type == 'match_type':  # Подсчёт вопросов на сопоставление
                    question_points = question.points
                    record_match_answers = ''
                    for answer in Answers.objects.filter(question_id__id=question.id).exclude(
                            match__exact=''):  # ??перебираем только "правильные" ответы, отрезая пустышку без match
                        student_answer = request.POST.get(str(answer.id))
                        record_match_answers = self.add_answer_to_record(record_match_answers, student_answer, ', ')
                        if student_answer != answer.answer:
                            question_points -= 1
                    if question_points > 0:
                        total_test_points += question_points
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, question_points)
                    else:
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                    record_to_add = record_match_answers
                elif question.question_type == 'input_type':  # Подсчет вопросов с вводом
                    answer = Answers.objects.get(question_id__id=question.id)
                    answers = str(answer.answer)
                    right_answers = list(answers.split(','))
                    student_answer = str(request.POST.get(str(answer.id)))
                    if student_answer in right_answers:
                        total_test_points += question.points
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, question.points)
                    else:
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                    record_to_add = 'No answer' if len(student_answer) == 0 else student_answer
                elif question.question_type == 'true_false_type':  # Подсчет вопросов с True/False
                    try:
                        if request.POST.get(str(question.id)) == Questions.objects.get(id=question.id).addition_after:      # .addition
                            total_test_points += question.points
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, question.points)
                        else:
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                    except:
                        pass
                    pass
                    record_to_add = 'No answer' if request.POST.get(str(question.id)) == None else request.POST.get(str(question.id))
                else:       # Подсчет вопросов с выбором
                    try:  # потому что студент может оставить radio невыбранным
                        answer_object = Answers.objects.get(pk=request.POST.get(str(question.id)))
                        if answer_object.is_true:
                            total_test_points += question.points
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, question.points)
                        else:
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                        record_to_add = answer_object.answer                # добавление ответа в запись
                    except:
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                        record_to_add = 'No answer'                         # добавление ответа в запись
                record_test_answers += (str(question.question_number) + ') ' + record_to_add + '; ')
            else:  # Writing and Speaking
                '''Создаем объект задания для проверки'''
                task_to_check = TasksToCheck()
                try:
                    media1_index = str(question.id) + '_media1'
                    media1 = request.FILES[media1_index]
                    #audio_data = base64.b64decode(media1)
                    #task_to_check.media1 = audio_data
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

                #print(task_to_check.media1.path)
                ## convert file here
                #wav_path = task_to_check.media1.path
                #mp3_path = task_to_check.media1.path.replace('.wav', '.mp3')
                #self.convert_wav_to_mp3(wav_path, mp3_path)
                ## You can use the mp3_path variable to do further operations if needed
                #print(f"Converted {wav_path} to {mp3_path}")


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
        result.detailed_points = detailed_test_points
        result.record_answers = record_test_answers
        result.time = str(timedelta(seconds=test_time))
        result.save()
        return HttpResponseRedirect('/test_result_with_points/' + str(result.pk) + '/')


class TestResultWOPoints(LoginRequiredMixin, ConfirmStudentMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/test_result_wo_points.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wait for results'
        return context


class TestResultWithPoints(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
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


# need decorator for checking student confirmation - to show only bb docs, not olymp
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


class Playaudio(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = OlympWay
    template_name = 'galaxy/play_audio.html'
    pk_url_kwarg = 'classes_id'
    context_object_name = 'file'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '_'.join(('Olymp', context['file'].year, context['file'].classes))
        return context


class Idioms(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'idioms'
        return context


def julik(request):
    return render(request, 'galaxy/julik.html')


class ShowTests(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 10
    model = Tests
    template_name = "galaxy/show_tests.html"
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Available Tests'
        context['pagination_number'] = self.paginate_by
        return context

    def get_queryset(self):
        self.template_name = "galaxy/show_assessment_tests.html" if self.kwargs.get('assessment_fl') == 1 \
            else "galaxy/show_tests.html"
        flag = True if self.kwargs.get('assessment_fl') == 1 else False
        #return Tests.objects.all().order_by('type', 'part', 'test_num')
        return Tests.objects.filter(is_assessment=flag).order_by('type', 'part', 'test_num')


class ShowTestsToCheck(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 15
    model = TestsToCheck
    template_name = "galaxy/show_tests_to_check.html"
    context_object_name = 'tests_to_check'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tests to check'         # needed??
        context['pagination_number'] = self.paginate_by
        return context

    def get_queryset(self):
        return TestsToCheck.objects.filter(is_checked=False)


class ShowCheckedTests(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 15
    model = TestsToCheck
    template_name = "galaxy/show_checked_tests.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tests to check'         # needed??
        context['pagination_number'] = self.paginate_by
        context['tests_to_check'] = {x: self.forming_query(x) for x in TestsToCheck.objects.filter(is_checked=True)}
        return context

    @staticmethod
    def forming_query(test):
        tasks = TasksToCheck.objects.filter(test_to_check_id=test)
        return sum(int(x.points) for x in tasks)


class ShowConfirmedStudents(LoginRequiredMixin, ConfirmMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/show_confirmed_students.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirmed Students'
        context['pagination_number'] = self.paginate_by
        group_list = Groups.objects.all()
        context['group_list'] = group_list
        return context

    def get_queryset(self):
        return self.foo(True)


class ShowPendingStudents(LoginRequiredMixin, ConfirmMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/show_pending_students.html"

    def get_queryset(self):
        return self.foo(None)


class ShowDeniedStudents(LoginRequiredMixin, ConfirmMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/show_denied_students.html"

    def get_queryset(self):
        return self.foo(False)


@user_passes_test(teacher_check, login_url='home')
def deny_student(request, student_id, template):
    student = CustomUser.objects.get(id=student_id)
    student.is_confirmed = False
    student.group = None
    student.save()
    return redirect(reverse_lazy(template))


@user_passes_test(teacher_check, login_url='home')
def confirm_student(request, student_id, template):
    student = CustomUser.objects.get(id=student_id)
    student.is_confirmed = True
    student.save()
    return redirect(reverse_lazy(template))


class CheckingTest(LoginRequiredMixin, TeacherUserMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
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


class AddTestAndChaptersView(LoginRequiredMixin, TeacherUserMixin, AddTestConstValues, AddChapterConstValues, View):
    login_url = '/login/'
    redirect_field_name = 'login'
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
            test_assessment_flag = test_obj.is_assessment
            test_num = Tests.objects.filter(type=test_type, part=test_part, is_assessment=test_assessment_flag).count() + 1
            test_obj.test_num = test_num
            test_obj.save()                                     # Save the Test
            self.add_test_const_values(test_obj)

            if len(chapter_formset.forms) == 0:     # auto adding 1 chapter
                chapter_obj = Chapters()
                chapter_obj.test_id = test_obj
                chapter_obj.chapter_number = 1
                chapter_obj.save()
            else:
                for chapter_form in chapter_formset.forms:          # Save the Chapters
                    if chapter_form.has_changed():
                        chapter_obj = chapter_form.save(commit=False)
                        chapter_obj.test_id = test_obj
                        chapter_obj.save()
                        if test_obj.part == 'Writing':
                            self.add_chapter_const_valuse(chapter_obj)

            return redirect('add_q_and_a', chapter_obj.id)

        context = {
            'test_form': test_form,
            'chapter_formset': chapter_formset,
        }
        return render(request, 'galaxy/add_test.html', context)


class AddQandAView(LoginRequiredMixin, TeacherUserMixin, ChooseAddQuestForm, AddQuestionConstValues, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    used_form = QuestionAddForm

    def get(self, request, *args, **kwargs):
        chapter_id = self.kwargs.get('chapter_id')
        question_form = self.choose_form(Chapters.objects.get(id=chapter_id))
        self.used_form = question_form
        answer_formset = formset_factory(AnswerAddForm, extra=0)
        context = {
            'question_form': question_form,
            'answer_formset': answer_formset,
        }

        return render(request, 'galaxy/add_q_and_a.html', context)

    def post(self, request, *args, **kwargs):
        chapter_id = self.kwargs.get('chapter_id')
        chapter_obj = Chapters.objects.get(id=chapter_id)
        sum_of_questions = Questions.objects.filter(test_id=chapter_obj.test_id).count()
        self.used_form = self.choose_form(chapter_obj)
        question_form = self.used_form(request.POST, request.FILES)
        print(self.used_form)
        answer_formset = formset_factory(AnswerAddForm, extra=0)(request.POST, request.FILES)
        if question_form.is_valid() and answer_formset.is_valid():
            question_obj = question_form.save(commit=False)
            question_obj.test_id = chapter_obj.test_id
            question_obj.chapter_id = chapter_obj
            question_obj.question_number = sum_of_questions + 1
            test_obj = chapter_obj.test_id
            self.add_question_points(question_obj)
            if test_obj.part == 'Speaking':
                self.add_question_timings(question_obj)     # adding time_limit and preparation_time
                # Test time limit for speaking depends on questions time limit and preparation time
                test_obj.time_limit += (question_obj.time_limit + question_obj.preparation_time)
                test_obj.save()
            if test_obj.part in 'Speaking, Writing':
                question_obj.question_type = 'file_adding_type'
            # If question has audio media set time_limit exact as length of media
            if test_obj.part == 'Speaking' and str(question_obj.media)[-3:] in ['wav', 'mp3', 'aac']:
                audio = MP3(question_obj.media)
                question_obj.time_limit = int(audio.info.length)
            # Save the question
            question_obj.save()

            # Save the Answers
            for answer_form in answer_formset.forms:
                if answer_form.has_changed():
                    answer_obj = answer_form.save(commit=False)
                    if question_obj.question_type == 'input_type':
                        answer_obj.answer = answer_obj.answer.upper()

                    answer_obj.question_id = question_obj
                    answer_obj.save()

            return redirect('add_q_and_a', chapter_id)


class ShowTest(LoginRequiredMixin, TeacherUserMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, test_pk):
        test = get_object_or_404(Tests, id=test_pk)

        content_dict = {}
        chapters_for_test = Chapters.objects.filter(test_id__id=test.id).order_by('chapter_number')
        for chapter in chapters_for_test:
            questions_for_test = Questions.objects.filter(chapter_id__id=chapter.id).order_by('question_number')
            qa = {}
            for question in questions_for_test:
                if question.question_type == 'match_type':
                    test_obj = question.test_id
                    if test_obj.type == 'USE' and test_obj.part == 'Listening' and question.question_number == 2:
                        qa[question] = {
                            key: Answers.objects.filter(question_id__id=question.id).order_by('answer').values_list(
                                'addition',
                                flat=True)
                            for key in
                            Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').
                                order_by('match')}
                    else:
                        qa[question] = {
                            key: Answers.objects.filter(question_id__id=question.id).order_by('answer').values_list(
                                'answer',
                                flat=True)
                            for key in
                            Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').
                                order_by('match')}
                elif question.question_type == 'input_type':
                    qa[question] = Answers.objects.get(question_id__id=question.id)     # незачем запрашивать?
                else:
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
            content_dict[chapter] = qa

        context = {'test': test,
                   'content_dict': content_dict,
                   }

        return render(request, 'galaxy/show_test.html', context)


class ShowColouredResult(LoginRequiredMixin, View):                    # exact copy of previous (inherit it?)
    login_url = '/login/'
    redirect_field_name = 'login'
    def get(self, request, result_pk):
        result_object = Results.objects.get(id=str(result_pk))
        test = get_object_or_404(Tests, id=result_object.test_id.id)

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
        print(content_dict)
        return render(request, 'galaxy/show_colour_result.html', context)


#def testing_page(request):
#    return render(request, 'galaxy/audio_recording_test.html')


class TestingPage(View):        # wtf is this
    template_name = 'galaxy/testing.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if len(request.FILES) > 0:
            return render(request, 'galaxy/index.html')
        else:
            # Render an error page
            return render(request, 'galaxy/julik.html')


class MakeAnAssessment(LoginRequiredMixin, TeacherUserMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = 'galaxy/make_an_assessment.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Make an assessment'
        group_list = Groups.objects.all().order_by('name')
        context['group_list'] = group_list
        return context

    def post(self, request, *args, **kwargs):
        group = Groups.objects.get(id=request.POST['group'])
        assessment_date = request.POST['datepicker']  # 06/09/2023
        assessment_date = datetime.strptime(assessment_date, "%m/%d/%Y").date()

        '''Собираем свободные тесты для ассессмента по типам '''
        assessment_tests_by_part = []
        for part in ['Grammar and Vocabulary', 'Listening', 'Reading', 'Speaking', 'Writing']:
            assessment_tests_by_part.append(
                Tests.objects.filter(is_assessment=True, type=group.test_type, part=part).
                exclude(used_in_groups__contains=group.name)
                                       )

        '''Проверяем на каждый ли тип теста есть свободный тест для назначения'''
        if len(assessment_tests_by_part) != 5:
            print('НЕ ХВАТАЕТ ТИПОВ АССЕССМЕНТА:', len(assessment_tests_by_part))
            return redirect('make_an_assessment')

        '''Назначение даты 5 рандомным тестам '''
        for test_query in assessment_tests_by_part:
            '''Уведомление о том, что осталось мало свободных ассессментов для этой группы'''
            if len(test_query) < 3:
                pass        # notification, that few tests left

            '''Назначение даты 5 рандомным тестам '''
            if len(test_query) > 0:
                random_test = test_query.order_by('?')[0]       # rly random or everytime the same?
                list_used_in_groups = random_test.used_in_groups.split(', ')
                if list_used_in_groups == ['']:
                    random_test.used_in_groups = group.name
                else:
                    list_used_in_groups.append(group.name)
                    random_test.used_in_groups = ', '.join(list_used_in_groups)
                random_test.save()
                assessment = Assessments(test=random_test, group=group, date=assessment_date)
                assessment.save()
        return redirect('show_current_assessments')


class ShowCurrentAssessments(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_current_assessments.html"

    def get_queryset(self):
        #return Tests.objects.exclude(appointed_to_group=None)
        return Assessments.objects.filter(is_passed=False).distinct('group', 'date')


@user_passes_test(teacher_check, login_url='home')
def delete_an_assessment(request, assessment_id):
    assessment_object = Assessments.objects.get(id=assessment_id)
    group = assessment_object.group
    date = assessment_object.date
    assessments_to_delete = Assessments.objects.filter(group=group, date=date)
    for assessment in assessments_to_delete:
        assessment.is_passed = True
        assessment.save()

    return redirect('show_current_assessments')


class ShowPastAssessments(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_past_assessments.html"

    def get_queryset(self):
        #return Tests.objects.exclude(appointed_to_group=None)
        return Assessments.objects.filter(is_passed=True).distinct('group', 'date')


class ShowAssessmentResults(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = CustomUser
    context_object_name = 'assessment_contestants'
    template_name = "galaxy/show_assessment_results.html"

    def get_queryset(self):
        assessment = Assessments.objects.get(id=self.kwargs.get('assessment_pk'))
        group = assessment.group
        users = CustomUser.objects.filter(group=group)
        assessments = Assessments.objects.filter(group=group, date=assessment.date).order_by("test__part")
        print(assessments)
        tests = [assessment.test for assessment in assessments]
        print({user: [Results.objects.get(student_id=user, test_id=test)
                      if Results.objects.filter(student_id=user, test_id=test).exists()
                      else "no result" for test in tests] for user in users})
        return {user: [Results.objects.filter(student_id=user, test_id=test) for test in tests] for user in users}
        #return CustomUser.objects.filter(group=group)


class ShowStudentAssessments(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_student_assessments.html"

    def get_queryset(self):
        user = self.request.user
        today = date.today()
        print([int(id_) for id_ in user.assessments_passed.split(',') if id_])
        return Assessments.objects.filter(group=user.group, date=today)\
            .exclude(test_id__in=[int(id_) for id_ in user.assessments_passed.split(',') if id_])


class ShowStudentAssessmentResults(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    #model = Results
    context_object_name = 'assessments'
    template_name = "galaxy/show_student_assessment_results.html"

    def get_queryset(self):
        user = self.request.user
        user_assessment_dates = [x.date for x in Assessments.objects.filter(group=user.group).distinct('date')]
        assessments_dict = {key: [Results.objects.get(student_id=user, test_id=x.test)
                                  if Results.objects.filter(student_id=user, test_id=x.test).exists()
                                  else "no result"
                                  for x in Assessments.objects.filter(group=user.group, date=key).order_by('test__part')]
                                  for key in user_assessment_dates}

        return assessments_dict


class Debug(View):
    template_name = 'galaxy/debug.html'

    def get(self, request):
        print('!!!!!!!!!!!!!!!!! DEBUG GET !!!!!!!!!!!!!!!!!!!')
        return render(request, self.template_name)

    def post(self, request):
        print('!!!!!!!!!!!!!!!!! DEBUG POST !!!!!!!!!!!!!!!!!!!')
        print(request.FILES)
        audio_file = request.FILES['audio']
        #print(type(audio_file))
        #audio_data = base64.b64decode(file)
        #print(type(audio_data))
        #print(os.path)

        destination_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'recorded.wav')
        print(destination_path)
        with open(destination_path, 'wb') as destination_file:
            for chunk in audio_file.chunks():
                destination_file.write(chunk)

        # Define a path to save the audio file
        #file_path = os.path.join('path_to_your_desired_directory', 'audio_file.wav')

        # Save the audio data to a file
        #with open(file_path, 'wb') as audio_file:
        #    audio_file.write(audio_data)

        response_data = {'message': 'POST request processed successfully'}
        return JsonResponse(response_data)
        #return redirect('home')

