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
from .utils import *
from django.contrib.auth.views import PasswordResetView
from pydub import AudioSegment
import base64
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Index(TemplateView, LoginRequiredMixin):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # tests_to_check = TestsToCheck.objects.filter(is_checked=False)
        context['title'] = 'Main Page'
        # context['tests_to_check'] = tests_to_check
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
        user = form.save()  # сохраняем форму в бд
        self.send_email_activation(user, self.request)
        return render(self.request,
                      'galaxy/email_check_page.html')  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! прямой редирект?????


def email_check_page(request):  # !!!!!!!!!!!!!!!!!!!!!!!!! без этой функции?
    return render(request, 'galaxy/email_check_page.html')


def verify_email(request, uid64, token):  # попадаем сюда из письма на почту
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

    def get_success_url(self):  # при успешном логине перенаправляет
        if not self.request.user.is_email_verified:
            logout(self.request)
            return reverse_lazy('email_check_page')

        # return reverse_lazy('personal_acc', kwargs={'acc_slug': self.request.user.slug})
        return reverse_lazy('home')


def logout_user(request):
    logout(request)  # станд функция выхода
    return redirect('home')


class ResetPassView(PasswordResetView):
    template_name = 'galaxy/password_reset.html'
    email_template_name = 'galaxy/password_reset_email.html'
    # subject_template_name = 'password_reset_subject'
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
    paginate_by = 10
    model = Results
    template_name = "galaxy/show_results.html"
    context_object_name = 'results'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My results'
        context['pagination_number'] = self.paginate_by
        tests = [x.test_id for x in Results.objects.filter(student_id=self.request.user).distinct('test_id')]
        context['dict'] = {key: 20 if key.type == 'USE' and key.part == 'Writing'
        else Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
                           for key in tests}
        return context

    def get_queryset(self):
        return Results.objects.filter(student_id=self.request.user, test_id__is_assessment=False)


class ResultSummary(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Results
    template_name = 'galaxy/result_summary.html'
    pk_url_kwarg = 'result_id'
    context_object_name = 'result'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Result commentary'
        result_id = self.kwargs['result_id']
        result_obj = Results.objects.get(id=result_id)
        result_commentary = str(result_obj.record_answers)
        context['commentary'] = [x for x in result_commentary.split(';')]
        return context


class ResultPreview(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Results
    template_name = 'galaxy/result_preview.html'
    pk_url_kwarg = 'result_id'
    context_object_name = 'result'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Result preview'
        result_id = self.kwargs['result_id']
        result_obj = Results.objects.get(id=result_id)
        test = get_object_or_404(Tests, id=result_obj.test_id.id)
        tasks_to_check = {quest_obj: TasksToCheck.objects.get
        (test_to_check_id=result_obj.test_to_check, question_id=quest_obj)
                          for quest_obj in
                          [x.question_id for x in
                           TasksToCheck.objects.filter(test_to_check_id=result_obj.test_to_check)]}

        context['tasks_to_check'] = tasks_to_check
        context['test'] = test
        chapters_for_test = Chapters.objects.filter(test_id__id=test.id).order_by('chapter_number')
        content_dict = {}
        for chapter in chapters_for_test:
            questions = Questions.objects.filter(chapter_id__id=chapter.id).order_by('question_number')
            content_dict[chapter] = questions
        context['content_dict'] = content_dict
        return context


class ShowColouredResult(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, result_pk):
        result_object = Results.objects.get(id=str(result_pk))
        test = get_object_or_404(Tests, id=result_object.test_id.id)
        # forming student_answers_dict
        result_record_answers = str(result_object.record_answers)
        temp_list = [x.lstrip(' ') for x in result_record_answers.split(';')]
        student_answers_dict = {int(x.split(') ')[0]): {y.split('-')[0]: y.split('-')[1]
                                                        for y in x.split(') ')[1].split(', ')}
        if '-' in x.split(') ')[1]
        else x.split(') ')[1] for x in temp_list[:-1]}

        right_answers_dict = {}
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
                    right_answers_dict[question.question_number] = \
                        {answer.match: answer.answer for answer in Answers.objects.filter(question_id__id=question.id)}

                elif question.question_type == 'input_type':
                    qa[question] = Answers.objects.get(question_id__id=question.id)
                    right_answers_dict[question.question_number] = \
                        (Answers.objects.get(question_id__id=question.id)).answer.split(',') if \
                            ',' in (Answers.objects.get(question_id__id=question.id)).answer else \
                            (Answers.objects.get(question_id__id=question.id)).answer
                elif question.question_type == 'single_choice_type':
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
                    right_answers_dict[question.question_number] = (
                        Answers.objects.get(question_id__id=question.id, is_true=True)).answer
                else:  # true/false
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
                    right_answers_dict[question.question_number] = Questions.objects.get(id=question.id).addition_after
            content_dict[chapter] = qa

        context = {'test': test,
                   'content_dict': content_dict,
                   'student_answers_dict': student_answers_dict,
                   'right_answers_dict': right_answers_dict,
                   }

        return render(request, 'galaxy/show_colour_result.html', context)


class ShowGroups(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Groups
    context_object_name = 'groups'
    template_name = "galaxy/show_groups.html"

    def get_queryset(self):
        return Groups.objects.all()


# @user_passes_test(teacher_check)
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
        #old_name = group_obj.name
        group_obj.name = new_name
        group_obj.save()
        '''change group name in assessment tests'''
        #tests_objects = Tests.objects.filter(used_in_groups__contains=old_name)
        #for test in tests_objects:
        #    groups_list = test.used_in_groups.split(', ')
        #    groups_list.remove(old_name)
        #    groups_list.append(new_name)
        #    test.used_in_groups = ', '.join(groups_list)
        #    test.save()
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


class UserProfile(LoginRequiredMixin, TeacherUserMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = CustomUser
    template_name = "galaxy/user_profile.html"
    pk_url_kwarg = 'user_pk'
    context_object_name = 'student'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.get(id=context['student'].pk)
        # counting results data
        user_results = Results.objects.filter(student_id=user.id, test_id__is_assessment=False)
        test_points = {'GSEListening': 15,
                       'GSEReading': 13,
                       'GSEGrammar and Vocabulary': 15,
                       'GSEWriting': 10,
                       'GSESpeaking': 15,
                       'USEListening': 12,
                       'USEReading': 12,
                       'USEGrammar and Vocabulary': 18,
                       'USEWriting': 20,
                       'USESpeaking': 20,
                       }

        avg_dict = [round(100 * (int(r.points) / test_points[r.test_id.type + r.test_id.part])) for r in user_results]
        avg_result = int(sum(avg_dict) / len(avg_dict)) if len(avg_dict) > 0 else 0
        context['avg_result'] = avg_result
        # counting assessments data
        user_assessment_dates = Assessments.objects \
            .filter(group=user.group).order_by('date').distinct('date')
        assessment_dict = {x: Assessments.objects.filter(date=x.date) for x in user_assessment_dates}
        content_dict = {x: [Results.objects.get(test_id=y.test, student_id=user)
                            if Results.objects.filter(student_id=user, test_id=y.test).exists()
                            else "no result" for y in assessment_dict[x]]
                        for x in assessment_dict.keys()}

        # counting %
        avg_list = []
        for results in content_dict.values():
            cleared_list = [i for i in results if i != 'no result']
            sum_of_points = sum([int(result.points) for result in cleared_list])
            avg_list.append(round(sum_of_points / 0.82))
        avg_assessment = int(sum(avg_list) / len(avg_list)) if len(avg_list) else 0

        context['avg_assessment'] = avg_assessment

        context['results'] = user_results
        context['assessments'] = user_assessment_dates
        context['title'] = user.first_name + user.last_name
        return context


class ShowUserResults(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 10
    model = CustomUser
    template_name = "galaxy/show_results.html"
    context_object_name = 'results'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['user_pk']
        user = CustomUser.objects.get(id=user_id)
        user_results = Results.objects.filter(student_id=user.id, test_id__is_assessment=False)
        context['student'] = user
        context['dict'] = {key: Questions.objects.filter(test_id=key).aggregate(Sum('points'))['points__sum']
                           for key in Tests.objects.all()}
        context['pagination_number'] = self.paginate_by
        context['title'] = user.first_name + user.last_name + 'results'
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_pk']
        user = CustomUser.objects.get(id=user_id)
        return Results.objects.filter(student_id=user.id, test_id__is_assessment=False)


class ShowUserAssessments(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = CustomUser
    template_name = "galaxy/show_user_assessments.html"
    context_object_name = 'assessments'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['user_pk']
        user = CustomUser.objects.get(id=user_id)
        context['student'] = user
        # user_results = Results.objects.filter(student_id=user.id)
        # context['results'] = user_results
        context['title'] = user.first_name + user.last_name
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_pk']
        return form_assessment_dict(user_id)


@user_passes_test(teacher_check, login_url='home')
def delete_group(request, group_id):
    group = Groups.objects.get(id=group_id)
    #name_to_delete = group.name
    group.delete()
    #tests_with_group_in_list = Tests.objects.filter(used_in_groups__contains=name_to_delete)
    #for test in tests_with_group_in_list:
    #    groups_list = test.used_in_groups.split(', ')
    #    groups_list.remove(name_to_delete)
    #    test.used_in_groups = ', '.join(groups_list)
    #    test.save()
    return redirect('show_groups')


@user_passes_test(teacher_check, login_url='home')
def update_student_group(request):
    print('!!!!!!!!!!!!!!!!!!!')
    user = CustomUser.objects.get(id=request.GET.get('student'))
    user.group = Groups.objects.get(id=request.GET.get('group'))
    user.save()
    return JsonResponse({'success': True})


class TestDetails(LoginRequiredMixin, ConfirmStudentMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    # login_url = reverse_lazy('login')
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

        # if str(test.id) in user.assessments_passed:
        #    return render(request, 'galaxy/julik.html')
        # if test in [x. UserToAssessment.objects.filter(user=user)]

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
                # audio_media_fl = 0
                # if test.part == 'Speaking' and str(question.media)[-3:] in ['wav', 'mp3', 'aac']:
                #    audio_media_fl = 1
                if question.question_type == 'match_type':  # Если вопрос на сопоставление
                    if question.test_id.type == 'USE' and question.test_id.part == 'Listening' and question.question_number == 2:
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
                            Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').order_by(
                                'match')}
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
    def add_answer_to_record(record_to_add_in, answer_match, answer_to_add, separation_item):
        if len(record_to_add_in) > 0:
            record_to_add_in += separation_item
        if answer_to_add == 'Выберите ответ':
            answer_to_add = 'No answer'
        record_to_add_in += (str(answer_match) + '-' + answer_to_add)
        return record_to_add_in

    # @staticmethod
    # def convert_to_mp3(file_path):
    #    print('IM IN COVERT')
    #    import subprocess
    #    mp3_file_path = file_path.replace('.wav', '.mp3')
    #    # Use FFmpeg to convert the WAV file to MP3
    #    subprocess.run(["ffmpeg", "-i", file_path, mp3_file_path])
    #    print('IM OUT CONVERT')
    #    return mp3_file_path

    # @staticmethod
    # def convert_wav_to_mp3(wav_path, mp3_path):
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
        if 'no_attached_files' in request.session:  # if it remained from previous test
            del request.session['no_attached_files']

        if test.part == 'Writing' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')

        if test.part == 'Speaking' and len(request.FILES) == 0:
            request.session['no_attached_files'] = 1
            return HttpResponseRedirect('/test_result_wo_points/')
            # return JsonResponse({'empty_flag': 1})

        '''Creating test_to_check object and result object for it'''
        if test.part in ['Writing', 'Speaking']:
            test_to_check = TestsToCheck()
            test_to_check.test_id = test
            test_to_check.student_id = user
            test_to_check.save()
            result_obj = Results()
            result_obj.test_to_check = test_to_check
            result_obj.time = str(timedelta(seconds=test_time))
            result_obj.save()

        # if test.is_assessment:
        #    if len(user.assessments_passed) > 0:
        #        user.assessments_passed += ','
        #    user.assessments_passed += str(test.id)
        #    user.save()
        if test.is_assessment:
            assessment_obj = Assessments.objects.filter(test=test, group=user.group)
            user_to_assessment_obj = UserToAssessment(user=user, assessment=assessment_obj)
            user_to_assessment_obj.save()


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
                        record_match_answers = self.add_answer_to_record(record_match_answers, answer.match,
                                                                         student_answer, ', ')
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
                    right_answers = [x.strip() for x in list(answers.split(','))]
                    print(right_answers)
                    student_answer = str(request.POST.get(str(answer.id)))
                    if student_answer in right_answers:
                        total_test_points += question.points
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, question.points)
                    else:
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                    record_to_add = 'No answer' if len(student_answer) == 0 else student_answer
                elif question.question_type == 'true_false_type':  # Подсчет вопросов с True/False
                    try:
                        if request.POST.get(str(question.id)) == Questions.objects.get(
                                id=question.id).addition_after:  # .addition
                            total_test_points += question.points
                            detailed_test_points = self.add_detail_points(question, detailed_test_points,
                                                                          question.points)
                        else:
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                    except:
                        pass
                    pass
                    record_to_add = 'No answer' if request.POST.get(str(question.id)) == None else request.POST.get(
                        str(question.id))
                else:  # Подсчет вопросов с выбором
                    try:  # потому что студент может оставить radio невыбранным
                        answer_object = Answers.objects.get(pk=request.POST.get(str(question.id)))
                        if answer_object.is_true:
                            total_test_points += question.points
                            detailed_test_points = self.add_detail_points(question, detailed_test_points,
                                                                          question.points)
                        else:
                            detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                        record_to_add = answer_object.answer  # добавление ответа в запись
                    except:
                        detailed_test_points = self.add_detail_points(question, detailed_test_points, 0)
                        record_to_add = 'No answer'  # добавление ответа в запись
                record_test_answers += (str(question.question_number) + ') ' + record_to_add + '; ')
            else:  # Writing and Speaking
                '''Creating task_to_check objects'''
                task_to_check = TasksToCheck()
                try:
                    media1_index = str(question.id) + '_media1'
                    media1 = request.FILES[media1_index]
                    # audio_data = base64.b64decode(media1)
                    # task_to_check.media1 = audio_data
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
    media = settings.MEDIA_ROOT  # importing from settings
    obj = get_object_or_404(OlympWay, id=classes_id)  # get path from db
    filepath = os.path.join(media, str(obj.task))  # uniting path
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


class ShowTestsByPart(LoginRequiredMixin, ConfirmStudentMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Tests
    template_name = "galaxy/show_tests_by_part.html"
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Available Tests'
        context['pagination_number'] = self.paginate_by
        context['current_type'] = self.kwargs.get('part').split(',')[0]
        context['current_part'] = self.kwargs.get('part').split(',')[1].split(' ')[0]

        user_id = self.request.user
        data = self.kwargs.get('part').split(',')
        type = data[0]
        part = data[1]

        # Query to fetch all tests along with the best result points
        tests_with_results = Tests.objects.filter(type=type, part=part, is_assessment=False)
        best_result_dict = {}
        for test in tests_with_results:
            best_result_points_obj = Results.objects.filter(test_id=test.id,
                                                            student_id=user_id
                                                            ).order_by('-points')[:1]

            if len(best_result_points_obj) > 0:
                key = best_result_points_obj[0].test_id
                best_result_dict[key] = best_result_points_obj[0]
        context['best_result_dict'] = best_result_dict
        return context

    def get_queryset(self):
        user_id = self.request.user
        data = self.kwargs.get('part').split(',')
        type = data[0]
        part = data[1]

        tests_with_results = Tests.objects.filter(type=type, part=part, is_assessment=False)

        return tests_with_results


def filter_tests_by_part(request):
    data = dict()
    # Get parameters from AJAX request
    type = request.GET.get('type')
    part = request.GET.get('part')
    show_only_not_passed = request.GET.get('not_passed')
    user_id = request.user

    tests_with_results = Tests.objects.filter(type=type, part=part, is_assessment=False)

    best_result_dict = {}
    for test in tests_with_results:
        best_result_points_obj = Results.objects.filter(test_id=test.id,
                                                        student_id=user_id
                                                        ).order_by('-points')[:1]

        if len(best_result_points_obj) > 0:
            key = best_result_points_obj[0].test_id
            best_result_dict[key] = best_result_points_obj[0]

    if show_only_not_passed == 'true':
        best_result_tests = best_result_dict.keys()
        best_result_test_ids = [test.id for test in best_result_tests]
        tests_with_results = tests_with_results.exclude(id__in=best_result_test_ids)

    context = {'tests': tests_with_results}
    context['best_result_dict'] = best_result_dict
    data['my_content'] = render_to_string('galaxy/render_table_tests_by_part.html',
                                          context, request=request)
    return JsonResponse(data)


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
        # return Tests.objects.all().order_by('type', 'part', 'test_num')
        return Tests.objects.filter(is_assessment=flag).order_by('type', 'part', 'test_num')


class ShowTestsAndAssessments(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    #paginate_by = 10
    model = Tests
    template_name = "galaxy/show_tests_and_assessments.html"
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Available Tests'
        context['current_category'] = 'Training'
        #context['pagination_number'] = self.paginate_by
        return context

    def get_queryset(self):
        return Tests.objects.filter(is_assessment=False).order_by('type', 'order', 'test_num')


def filter_tests_and_assessments(request):
    data = dict()
    # Get parameters from AJAX request
    value_dict = {'Assessment': True, 'Training': False}
    filter_flag = request.GET.get('filter_flag')
    flag_value = value_dict[filter_flag]

    checkboxes = request.GET.get('checkboxes')
    checkbox_values = checkboxes.split(',')
    if 'Grammar' in checkbox_values:
        checkbox_values.remove('Grammar')
        checkbox_values.append('Grammar and Vocabulary')
    if checkbox_values == ['ALL']:
        tests = Tests.objects.filter(is_assessment=flag_value).order_by('type', 'order', 'test_num')
    else:
        tests = Tests.objects.filter(is_assessment=flag_value)\
            .filter(type__in=checkbox_values, part__in=checkbox_values)\
            .order_by('type', 'order', 'test_num')

    context = {}
    context['tests'] = tests
    context['current_category'] = filter_flag
    data['my_content'] = render_to_string('galaxy/render_tests_and_assessments_table.html',
                                          context, request=request)

    return JsonResponse(data)


class ShowTestsToCheck(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 10
    model = TestsToCheck
    template_name = "galaxy/show_tests_to_check.html"
    context_object_name = 'tests_to_check'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tests to check'  # needed??
        context['current_category'] = 'ToCheck'
        context['pagination_number'] = self.paginate_by
        return context

    def get_queryset(self):
        return TestsToCheck.objects.filter(is_checked=False)


def filter_tests_to_check(request):
    data = dict()
    # Get parameters from AJAX request
    value_dict = {'Checked': True, 'ToCheck': False}
    filter_flag = request.GET.get('filter_flag')
    flag_value = value_dict[filter_flag]
    filter_value = request.GET.get('filter_value')
    tests_to_check = TestsToCheck.objects.filter(is_checked=flag_value).filter(
        Q(student_id__first_name__icontains=filter_value) |
        Q(student_id__last_name__icontains=filter_value) |
        Q(test_id__type__icontains=filter_value) |
        Q(test_id__part__icontains=filter_value)
    ).order_by('id')

    # Paginate the filtered tests
    paginator = Paginator(tests_to_check, 10)
    page_number = request.GET.get('page')
    try:
        paginated_tests = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_tests = paginator.page(1)
    except EmptyPage:
        paginated_tests = paginator.page(paginator.num_pages)

    context = {'tests_to_check': paginated_tests}
    context['current_category'] = filter_flag
    data['my_content'] = render_to_string('galaxy/render_tests_to_check_table.html',
                                          context, request=request)
    data['pagination_html'] = render_to_string('galaxy/pagination.html', {'page_obj': paginated_tests}, request=request)
    return JsonResponse(data)


class ShowCheckedTests(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 15
    model = TestsToCheck
    template_name = "galaxy/show_checked_tests.html"
    context_object_name = 'checked_tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tests to check'  # needed??
        context['pagination_number'] = self.paginate_by
        context['points'] = {x: self.forming_query(x) for x in TestsToCheck.objects.filter(is_checked=True)}
        return context

    @staticmethod
    def forming_query(test):
        tasks = TasksToCheck.objects.filter(test_to_check_id=test)
        return sum(int(x.points) for x in tasks)

    def get_queryset(self):
        return TestsToCheck.objects.filter(is_checked=True)


# class ShowConfirmedStudents(LoginRequiredMixin, ConfirmMixin, TeacherUserMixin, ListView):
#    login_url = '/login/'
#    redirect_field_name = 'login'
#    template_name = "galaxy/show_confirmed_students.html"
#
#    def get_context_data(self, *, object_list=None, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['title'] = 'Confirmed Students'
#        context['pagination_number'] = self.paginate_by
#        group_list = Groups.objects.all()
#        context['group_list'] = group_list
#        return context
#
#    def get_queryset(self):
#        return self.foo(True)


class ShowStudents(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/show_students.html"
    paginate_by = 10
    model = CustomUser
    context_object_name = 'students'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Students'
        context['pagination_number'] = self.paginate_by
        context['type_flag'] = 'Pending'
        context['group_list'] = Groups.objects.all()
        return context

    def get_queryset(self):
        return CustomUser.objects.filter(role='Student', is_confirmed=None).order_by('id')


def filter_students(request):
    data = dict()
    # Get parameters from AJAX request
    value_dict = {'Denied': False, 'Pending': None, 'Confirmed': True}
    type_flag = request.GET.get('type_flag')
    flag_value = value_dict[type_flag]
    filter_value = request.GET.get('filter_value')
    # Query to fetch all tests along with user's results and applying filters
    # students = CustomUser.objects.filter(role='Student', is_confirmed=flag_value).order_by('id')
    students = CustomUser.objects.filter(role='Student', is_confirmed=flag_value).filter(
        Q(username__icontains=filter_value) |
        Q(first_name__icontains=filter_value) |
        Q(last_name__icontains=filter_value)
    ).order_by('id')

    context = {'students': students}
    context['type_flag'] = type_flag
    context['group_list'] = Groups.objects.all()
    data['my_content'] = render_to_string('galaxy/render_students_table.html',
                                          context, request=request)
    return JsonResponse(data)


@user_passes_test(teacher_check, login_url='home')
def confirm_deny_student(request):
    student = CustomUser.objects.get(id=int(request.POST.get('student_id')))
    action = request.POST.get('action')
    operation_dict = {'confirm': True, 'deny': False}
    student.is_confirmed = operation_dict[action]
    student.group = None
    student.save()
    return JsonResponse({'success': True})


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
            try:
                sum_points_for_test += int(request.POST.get(index))
            except ValueError:
                pass
            task.save()
        test_to_check.is_checked = True
        test_to_check.save()

        '''Создание результата для отображения у ученика'''
        result = Results.objects.get(test_to_check=test_to_check)
        result.student_id = test_to_check.student_id
        result.test_id = test_to_check.test_id
        result.points = sum_points_for_test
        result.commentary = request.POST.get('commentary')
        result.test_to_check = test_to_check
        result.save()

        return redirect('show_tests_to_check')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'checking test'
        context['form'] = TaskCheckForm()  # не нужна?
        test_to_check = context['test_to_check']
        tasks_to_check = TasksToCheck.objects.filter(test_to_check_id=test_to_check)
        context['tasks_to_check'] = tasks_to_check
        return context


# def download(request, document_id):
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
            test_num = Tests.objects.filter(type=test_type, part=test_part,
                                            is_assessment=test_assessment_flag).count() + 1
            test_obj.test_num = test_num
            test_obj.save()  # Save the Test
            self.add_test_const_values(test_obj)

            if len(chapter_formset.forms) == 0:  # auto adding 1 chapter
                chapter_obj = Chapters()
                chapter_obj.test_id = test_obj
                chapter_obj.chapter_number = 1
                chapter_obj.save()
                first_chapter_obj = chapter_obj
            else:
                for chapter_form in chapter_formset.forms:  # Save the Chapters
                    if chapter_form.has_changed():
                        chapter_obj = chapter_form.save(commit=False)
                        chapter_obj.test_id = test_obj
                        chapter_obj.save()
                        self.add_chapter_const_value(chapter_obj)
                        # picking up first chapter in this test to add questions to it
                        first_chapter_obj = Chapters.objects.get(test_id=test_obj, chapter_number=1)

            return redirect('add_q_and_a', first_chapter_obj.id)

        context = {
            'test_form': test_form,
            'chapter_formset': chapter_formset,
        }
        return render(request, 'galaxy/add_test.html', context)


def edit_test(request):
    pass


def delete_test(request):
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        test = get_object_or_404(Tests, id=test_id)
        test.delete()
        return JsonResponse({'message': 'Test deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


class AddQandAView(LoginRequiredMixin, TeacherUserMixin, ChooseAddQuestForm, AddQuestionConstValues, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, *args, **kwargs):
        chapter_id = self.kwargs.get('chapter_id')
        question_form = self.choose_form('add', Chapters.objects.get(id=chapter_id))
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
        used_form = self.choose_form('add', chapter_obj)
        question_form = used_form(request.POST, request.FILES)
        answer_formset = formset_factory(AnswerAddForm, extra=0)(request.POST, request.FILES)
        if question_form.is_valid() and answer_formset.is_valid():
            question_obj = question_form.save(commit=False)
            question_obj.test_id = chapter_obj.test_id
            question_obj.chapter_id = chapter_obj
            question_obj.question_number = sum_of_questions + 1
            test_obj = chapter_obj.test_id
            self.add_question_points(question_obj)
            if test_obj.part == 'Speaking':
                self.add_question_timings(question_obj)  # adding time_limit and preparation_time
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


class EditTestData(LoginRequiredMixin, TeacherUserMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, *args, **kwargs):
        test_id = self.kwargs.get('test_id')
        test_obj = Tests.objects.get(id=test_id)
        test_form = TestAddForm
        test_form = test_form(instance=test_obj)

        context = {
            'test_form': test_form,
            'test': test_obj,
        }

        return render(request, 'galaxy/edit_test_data.html', context)

    def post(self, request, *args, **kwargs):
        test_id = self.kwargs.get('test_id')
        test_obj = Tests.objects.get(id=test_id)
        old_media_path = test_obj.media.path if test_obj.media else None
        test_form = TestAddForm
        test_form = test_form(request.POST, request.FILES, instance=test_obj)
        if test_form.is_valid():
            test_obj = test_form.save(commit=False)
            test_obj.save()
            if ('media' in request.FILES and old_media_path) or request.POST.get('media-clear') == 'on':
                if os.path.exists(old_media_path):
                    os.remove(old_media_path)

        # todo check redirect
        return redirect('test', 'edit', test_id)


class EditChapterData(LoginRequiredMixin, TeacherUserMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, *args, **kwargs):
        chapter_id = self.kwargs.get('chapter_id')
        chapter_obj = Chapters.objects.get(id=chapter_id)
        test_obj = chapter_obj.test_id
        chapter_form = EditChapterForm
        chapter_form = chapter_form(instance=chapter_obj)

        context = {
            'chapter_form': chapter_form,
            'test': test_obj,
        }

        return render(request, 'galaxy/edit_chapter_data.html', context)

    def post(self, request, *args, **kwargs):
        chapter_id = self.kwargs.get('chapter_id')
        chapter_obj = Chapters.objects.get(id=chapter_id)

        chapter_form = EditChapterForm
        chapter_form = chapter_form(request.POST, request.FILES, instance=chapter_obj)
        if chapter_form.is_valid():
            chapter_obj = chapter_form.save(commit=False)
            chapter_obj.save()

        # todo check redirect
        return redirect('test', 'edit', chapter_obj.test_id.id)


class EditQandAView(LoginRequiredMixin, TeacherUserMixin, ChooseAddQuestForm, AddQuestionConstValues, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, *args, **kwargs):
        from django.forms import modelformset_factory

        question_id = self.kwargs.get('question_id')
        question_obj = Questions.objects.get(id=question_id)
        question_form = self.choose_form('edit', Chapters.objects.get(id=question_obj.chapter_id.id))
        question_form = question_form(instance=question_obj)

        answer_objects = Answers.objects.filter(question_id=question_obj)
        answer_formset = modelformset_factory(Answers, AnswerAddForm, extra=0)
        formset = answer_formset(queryset=answer_objects)

        context = {
            'question_form': question_form,
            'answer_formset': formset,
            'test': question_obj.test_id,
        }

        return render(request, 'galaxy/edit_q_and_a.html', context)

    def post(self, request, *args, **kwargs):
        question_id = self.kwargs.get('question_id')
        question_obj = Questions.objects.get(id=question_id)
        question_form = self.choose_form('edit', Chapters.objects.get(id=question_obj.chapter_id.id))
        question_form = question_form(request.POST, request.FILES, instance=question_obj)

        answer_formset = modelformset_factory(Answers, AnswerAddForm)
        formset = answer_formset(request.POST, request.FILES)

        # deleting answers
        if request.POST.get('deleted_answer_ids', '') != '':
            deleted_answer_ids = request.POST.get('deleted_answer_ids', '').split(',')

            for answer_id in deleted_answer_ids:
                try:
                    answer = Answers.objects.get(pk=answer_id)
                    answer.delete()
                except Answers.DoesNotExist:
                    pass

        # saving question
        if question_form.is_valid() and formset.is_valid():
            question_obj = question_form.save(commit=False)
            question_obj.save()

            for answer_form in formset.forms:
                if answer_form.has_changed():
                    answer_obj = answer_form.save(commit=False)
                    if question_obj.question_type == 'input_type':
                        answer_obj.answer = answer_obj.answer.upper()

                    answer_obj.question_id = question_obj
                    answer_obj.save()
            # todo check redirect
            return redirect('test', 'edit', question_obj.test_id.id)

        return redirect('edit_q_and_a', question_id)


def delete_question(request, question_id):
    question_obj = Questions.objects.get(id=question_id)
    test_obj = question_obj.test_id
    questions = Questions.objects.filter(test_id=test_obj, question_number__gt=question_obj.question_number)
    for question in questions:
        question.question_number -= 1
        question.save()

    question_obj.delete()
    # todo change redirect
    return redirect('show_test', test_obj.id)


class ShowOrEditTest(LoginRequiredMixin, TeacherUserMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = "galaxy/show_test.html"

    def get(self, request, show_type, test_pk):
        test = get_object_or_404(Tests, id=test_pk)
        if show_type == 'edit':
            self.template_name = "galaxy/edit_test.html"
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
                            key: Answers.objects.filter(question_id__id=question.id).order_by('id').values_list(    #  # changed order_by('answer')
                                'answer',
                                flat=True)
                            for key in
                            Answers.objects.filter(question_id__id=question.id).exclude(match__exact='').
                                order_by('match')}
                elif question.question_type == 'input_type':
                    qa[question] = Answers.objects.get(question_id__id=question.id)  # незачем запрашивать?
                else:  #
                    qa[question] = Answers.objects.filter(question_id__id=question.id)
            content_dict[chapter] = qa

        context = {'test': test,
                   'content_dict': content_dict,
                   }

        return render(request, self.template_name, context)


# def testing_page(request):
#    return render(request, 'galaxy/audio_recording_test.html')


class TestingPage(View):  # wtf is this
    template_name = 'galaxy/testing.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if len(request.FILES) > 0:
            return render(request, 'galaxy/index.html')
        else:
            # Render an error page
            return render(request, 'galaxy/julik.html')


class ShowAssessmentsForTeacher(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_assessments_for_teacher.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Current assessments'
        group_list = Groups.objects.all().order_by('name')
        context['group_list'] = group_list
        context['current_category'] = 'Current'
        return context

    def get_queryset(self):
        # return Tests.objects.exclude(appointed_to_group=None)
        return Assessments.objects.filter(is_passed=False).distinct('group', 'date')


def filter_assessments_for_teacher(request):
    data = dict()
    # Get parameters from AJAX request
    value_dict = {'Current': False, 'Past': True}
    filter_flag = request.GET.get('filter_flag')
    flag_value = value_dict[filter_flag]

    assessments = Assessments.objects.filter(is_passed=flag_value).distinct('group', 'date')

    # Paginate the filtered tests
    paginator = Paginator(assessments, 10)
    page_number = request.GET.get('page')
    try:
        paginated_tests = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_tests = paginator.page(1)
    except EmptyPage:
        paginated_tests = paginator.page(paginator.num_pages)

    context = {'assessments': paginated_tests}
    context['current_category'] = filter_flag
    group_list = Groups.objects.all().order_by('name')
    context['group_list'] = group_list
    data['my_content'] = render_to_string('galaxy/render_assessments_table.html',
                                          context, request=request)
    data['pagination_html'] = render_to_string('galaxy/pagination.html', {'page_obj': paginated_tests}, request=request)
    return JsonResponse(data)


@user_passes_test(teacher_check, login_url='home')
def save_an_assessment(request):
    group = Groups.objects.get(id=request.GET.get('group'))
    assessment_date = request.GET.get('date')
    assessment_date = datetime.strptime(assessment_date, "%m/%d/%Y").date()

    '''Собираем свободные тесты для ассессмента по типам '''
    assessment_tests_by_part = []
    for part in ['Grammar and Vocabulary', 'Listening', 'Reading', 'Speaking', 'Writing']:
        # assessment_tests_by_part.append(
        #    Tests.objects.filter(is_assessment=True, type=group.test_type, part=part).
        #        exclude(used_in_groups__contains=group.name)
        # )
        from django.db.models import Subquery
        assessment_tests_by_part.append(
            Tests.objects.filter(is_assessment=True, type=group.test_type, part=part).
                exclude(id__in=Subquery(
                UsedTestsToGroups.objects.filter(group=group).values('test_id'))
            )
        )

    '''Проверяем на каждый ли тип теста есть свободный тест для назначения'''
    if len(assessment_tests_by_part) != 5:
        print('НЕ ХВАТАЕТ ТИПОВ АССЕССМЕНТА:', len(assessment_tests_by_part))
        return redirect('make_an_assessment')

    '''Назначение даты 5 рандомным тестам '''
    for test_query in assessment_tests_by_part:
        '''Уведомление о том, что осталось мало свободных ассессментов для этой группы'''
        if len(test_query) < 3:
            pass  # notification, that few tests left

        '''Назначение даты 5 рандомным тестам '''
        if len(test_query) > 0:
            random_test = test_query.order_by('?')[0]  # rly random or everytime the same?
            # list_used_in_groups = random_test.used_in_groups.split(', ')
            # if list_used_in_groups == ['']:
            #    random_test.used_in_groups = group.name
            # else:
            #    list_used_in_groups.append(group.name)
            #    random_test.used_in_groups = ', '.join(list_used_in_groups)
            # random_test.save()
            test_to_group_obj = UsedTestsToGroups(group=group, test=random_test)
            test_to_group_obj.save()
            assessment = Assessments(test=random_test, group=group, date=assessment_date)
            assessment.save()
    return JsonResponse({'success': True})


@user_passes_test(teacher_check, login_url='home')
def close_assessment(request):
    assessment_id = request.GET.get('id')
    assessment_object = Assessments.objects.get(id=assessment_id)
    group = assessment_object.group
    date = assessment_object.date
    assessments_to_delete = Assessments.objects.filter(group=group, date=date)
    for assessment in assessments_to_delete:
        assessment.is_passed = True
        assessment.save()

    return redirect('show_assessments')


class ShowAssessmentResults(LoginRequiredMixin, TeacherUserMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = CustomUser
    context_object_name = 'assessment_contestants'
    template_name = "galaxy/show_assessment_results.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment_obj = Assessments.objects.get(id=self.kwargs.get('assessment_pk'))
        context['title'] = str(assessment_obj.group) + 'assessment'
        context['assessment'] = assessment_obj
        return context

    def get_queryset(self):
        from django.db.models import Case, When, Value, CharField
        assessment = Assessments.objects.get(id=self.kwargs.get('assessment_pk'))
        group = assessment.group
        # users = [x if assessment.pk in x.assessment_passed for x in CustomUser.objects.filter(group=group)]
        users = CustomUser.objects.filter(group=group)
        right_order = ['Listening', 'Reading', 'Grammar and Vocabulary', 'Writing', 'Speaking']
        whens = [When(test__part=part, then=Value(i)) for i, part in enumerate(right_order)]
        assessments = Assessments.objects.filter(group=group, date=assessment.date).annotate(
            custom_order=Case(*whens, output_field=CharField())
        ).order_by('custom_order')
        tests = [assessment.test for assessment in assessments]  # 5 appointed tests

        temp_dict = {user: [Results.objects.get(student_id=user, test_id=test)
                            if Results.objects.filter(student_id=user, test_id=test).exists()
                            else 'no result'
                            for test in tests]
                     for user in users}
        # counting %
        for user, results in temp_dict.items():
            if assessment.test.type == 'USE':
                max_points = 82
            else:
                max_points = 68
            while len(results) < 5:
                results.append('no result')
            cleared_list = [i for i in results if i != 'no result']
            sum_of_points = sum([int(result.points) for result in cleared_list])
            results.append(str(sum_of_points) + '(' + str(max_points) + ')')
            results.append(str(round(sum_of_points / (max_points / 100))) + '%')
        return temp_dict


class ShowAssessmentsForStudent(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Assessments
    context_object_name = 'assessments'
    template_name = "galaxy/show_assessments_for_student.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Assessments'
        context['current_category'] = 'Planned'
        return context

    def get_queryset(self):
        user = self.request.user
        today = date.today()
        #todo need to show todays assessments
        return UserToAssessment.objects.filter(user=user).values_list('assessment', flat=True)
        #return Assessments.objects.filter(group=user.group, date=today) \
        #    .exclude(test_id__in=[int(id) for id in user.assessments_passed.split(',') if id])  # надо ли исключать?


def filter_assessments_for_student(request):
    data = dict()
    filter_flag = request.GET.get('filter_flag')
    user = request.user
    if filter_flag == 'Passed':
        assessments_dict = form_assessment_dict(user.id)
        context = {'assessments': assessments_dict}
    else:
        today = date.today()
        # todo need to show todays assessments
        assessments = UserToAssessment.objects.filter(user=user).values_list('assessment', flat=True)
        #assessments = Assessments.objects.filter(group=user.group, date=today) \
        #    .exclude(test_id__in=[int(id_) for id_ in user.assessments_passed.split(',') if id_])
        context = {'assessments': assessments}

    context['current_category'] = filter_flag
    data['my_content'] = render_to_string('galaxy/render_assessments_for_student.html',
                                          context, request=request)
    return JsonResponse(data)


class Debug(View):
    template_name = 'galaxy/debug.html'

    def get(self, request):
        print('!!!!!!!!!!!!!!!!! DEBUG GET !!!!!!!!!!!!!!!!!!!')
        return render(request, self.template_name)

    def post(self, request):
        print('!!!!!!!!!!!!!!!!! DEBUG POST !!!!!!!!!!!!!!!!!!!')
        print(request.FILES)
        audio_file = request.FILES['audio']
        # print(type(audio_file))
        # audio_data = base64.b64decode(file)
        # print(type(audio_data))
        # print(os.path)

        destination_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'recorded.wav')
        print(destination_path)
        with open(destination_path, 'wb') as destination_file:
            for chunk in audio_file.chunks():
                destination_file.write(chunk)

        # Define a path to save the audio file
        # file_path = os.path.join('path_to_your_desired_directory', 'audio_file.wav')

        # Save the audio data to a file
        # with open(file_path, 'wb') as audio_file:
        #    audio_file.write(audio_data)

        response_data = {'message': 'POST request processed successfully'}
        return JsonResponse(response_data)
        # return redirect('home')
