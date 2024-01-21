from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin

from galaxy.forms import *
from galaxy.models import CustomUser
from django.shortcuts import redirect

class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_email_verified)


generate_token = TokenGenerator()


class NotLoggedIn(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('home')

class ConfirmMixin:
    """Formation list of students, value in foo - True/False/None
    depending on type of students(confirmed/not confirmed/pending).
    q - parameters from search field"""
    paginate_by = 15
    model = CustomUser
    context_object_name = 'students'

    def foo(self, value):
        query = self.request.GET.get('q')
        if query:
            return CustomUser.objects.filter(role='Student', is_confirmed=value).filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        return CustomUser.objects.filter(role='Student', is_confirmed=value).order_by('id')


class TeacherUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'Teacher'

    def handle_no_permission(self):
        return redirect('home')


class ConfirmStudentMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_confirmed is True

    def handle_no_permission(self):
        return redirect('julik')


class AddTestConstValues:
    timings = {'GSEListening': 1800,
            'GSEReading': 1800,
            'GSEGrammar and Vocabulary': 1800,
            'GSESpeaking': 0,
            'GSEWriting': 1800,
            'USEListening': 1800,
            'USEReading': 1800,
            'USEGrammar and Vocabulary': 2400,
            'USESpeaking': 0,
            'USEWriting': 5400}

    texts = {'GSEListening': '''В разделе аудирования по ОГЭ Вам предлагается прослушать несколько текстов 
                             и выполнить 11 заданий на понимание прослушанных текстов. 
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный. 
                             Воспроизведение аудио-задания начнется автоматически, 
                             у Вас не будет возможности остановить(поставить на паузу) или отмотать аудиозапись. 
                             Настоятельно рекомендуем не обновлять страницу теста- 
                             в этом случае воспроизведение аудио задания начнется заново
                             и Вы не успеете прослушать её до конца до истечении таймера.''',

            'GSEReading': '''В разделе чтения по ОГЭ Вам предлагается выполнить 8 заданий на понимание прочитанных текстов.
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный.''',

            'GSEGrammar and Vocabulary': '''В разделе грамматики по ОГЭ Вам предлагается выполнить 15 заданий на понимание прочитанных текстов.
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный.''',

            'GSESpeaking': '''Устная часть КИМ ОГЭ по английскому языку включает в себя 3 задания.
                             Задание 1 предусматривает чтение вслух небольшого текста научно-популярного характера. 
                             Время на подготовку – 1,5 минуты.
                             В задании 2 предлагается принять участие в условном диалоге-расспросе: 
                             ответить на шесть услышанных в аудиозаписи вопросов телефонного опроса.
                             При выполнении задания 3 необходимо построить связноемонологическое высказывание 
                             на определённую тему с опорой на план.Время на подготовку – 1,5 минуты.
                             Общее время ответа одного участника ОГЭ (включая время на подготовку) – 15 минут. 
                             Каждое последующее задание выдаётся после окончания выполнения предыдущего задания. 
                             Постарайтесь полностью выполнить поставленные задачи,
                             говорить ясно и чётко, не отходить от темы и следовать предложенному плану ответа. 
                             Так Вы сможете набрать наибольшее количество баллов.''',

            'GSEWriting': '''Для ответа на задание по письму, Вам необходимо приготовить лист формата А4 и ручку. 
                             Вам будет необходимо написать от руки Ваш ответ, 
                             сфотографировать его и прикрепить фотографию в поле "Ответ". 
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста, 
                             этот таймер только для информации и после его окончания у Вас будет время прикрепить Ваш ответ.
                             Он рассчитан полностью на Вашу честность, что после окончания таймера Вы не будете дописывать письмо. 
                             Обратите внимание также на необходимость соблюдения указанного объёма электронного письма. 
                             Письмо недостаточного объёма, а также часть текста электронного письма, 
                             превышающая требуемый объём, не оцениваются.''',

            'USEListening': '''В разделе аудирования по ЕГЭ Вам предлагается прослушать несколько текстов 
                             и выполнить 9 заданий на понимание прослушанных текстов. 
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный. 
                             Воспроизведение аудио-задания начнется автоматически, 
                             у Вас не будет возможности остановить(поставить на паузу) или отмотать аудиозапись. 
                             Настоятельно рекомендуем не обновлять страницу теста- 
                             в этом случае воспроизведение аудио задания начнется заново
                             и Вы не успеете прослушать её до конца до истечении таймера. ''',

            'USEReading': '''В разделе чтения по ЕГЭ Вам предлагается выполнить 9 заданий на понимание прочитанных текстов.
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный. ''',

            'USEGrammar and Vocabulary': '''В разделе грамматики по ОГЭ Вам предлагается выполнить 18 заданий на понимание прочитанных текстов.
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный.''',

            'USESpeaking': ''' ''',

            'USEWriting': '''Для ответа на задание по письму, Вам необходимо приготовить 2 листа формата А4 и ручку. 
                             Вам будет необходимо написать от руки Ваш ответ, сфотографировать его 
                             и прикрепить фотографии в поле "Ответ". 
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста, 
                             этот таймер только для информации и после его окончания у Вас будет время прикрепить Ваши ответы.
                             Он рассчитан полностью на Вашу честность, что после окончания таймера Вы не будете дописывать письмо.
                             Обратите внимание также на необходимость соблюдения указанного объёма электронного письма. 
                             Письмо недостаточного объёма, а также часть текста электронного письма, 
                             превышающая требуемый объём, не оцениваются.'''}

    def add_test_const_values(self, test_obj):
        test_obj.time_limit = self.timings[test_obj.type + test_obj.part]
        test_obj.test_details = self.texts[test_obj.type + test_obj.part]
        test_obj.save()


class AddChapterConstValues:
    info = {'USEWriting1': '''Для ответов на задания 1 и 2 используйте листы формата А4. 
                              Запишите на них свои ответы, сфотографируйте и прикрепите каждый под своим заданием в поле ответа. 
                              Черновики прикреплять не надо.
                              Обратите внимание также на необходимость соблюдения указанного объёма текста. Тексты
                              недостаточного объёма, а также часть текста, превышающая требуемый объём, не оцениваются.''',
            'USEWriting2': '''Выберите только ОДНО из двух предложенных заданий (2.1 или 2.2), 
                              укажите его номер в БЛАНКЕ ОТВЕТА и выполните согласно данному плану. 
                              В ответе на задание 2 числительные пишите цифрами.'''}

    def add_chapter_const_valuse(self, chapter_obj):
        chapter_obj.info = self.info[chapter_obj.test_id.type +
                                     chapter_obj.test_id.type +
                                     str(chapter_obj.chapter_number)]


class AddQuestionConstValues:
    question_preparation_times = {'USESpeaking1': 90,
                                  'USESpeaking2': 90,
                                  'USESpeaking3': 0,
                                  'USESpeaking4': 150,
                                  'GSESpeaking1': 90,
                                  'GSESpeaking2': 0,
                                  'GSESpeaking3': 90,
                                  }

    question_time_limits = {'USESpeaking1': 90,
                            'USESpeaking2': 80,
                            'USESpeaking3': 0,
                            'USESpeaking4': 180,
                            'GSESpeaking1': 120,
                            'GSESpeaking2': 0,
                            'GSESpeaking3': 120,
                            }

    question_points = {'USESpeaking1': 1,
                       'USESpeaking2': 4,
                       'USESpeaking3': 5,
                       'USESpeaking4': 10,
                       'GSESpeaking1': 2,
                       'GSESpeaking2': 6,
                       'GSESpeaking3': 7,
                       'GSEListening5': 5,
                       'GSEReading1': 6,
                       'USEListening1': 2,
                       'USEListening2': 3,
                       'USEReading1': 3,
                       'USEReading2': 2,
                       'USEWriting1': 6,
                       'USEWriting2': 14,
                       'USEWriting3': 14,
                       'GSEWriting1': 10,
                       }

    def add_question_timings(self, question_obj):
        question_obj.preparation_time = self.question_preparation_times[question_obj.test_id.type +
                                                                           question_obj.test_id.part +
                                                                           str(question_obj.question_number)]
        question_obj.time_limit = self.question_time_limits[question_obj.test_id.type +
                                                               question_obj.test_id.part +
                                                               str(question_obj.question_number)]
        question_obj.save()

    def add_question_points(self, question_obj):
        key = question_obj.test_id.type + question_obj.test_id.part + str(question_obj.question_number)
        if key in self.question_points.keys():
            question_obj.points = self.question_points[key]
        else:
            question_obj.points = 1
        question_obj.save()


class ChooseAddQuestForm:
    def choose_form(self, chapter_object):
        if chapter_object.test_id.part == 'Writing':
            return WritingQandAAddForm
        elif chapter_object.test_id.part == 'Speaking':
            return SpeakingQandAAddForm
        else:
            return QuestionAddForm


def teacher_check(user):
    return user.role == 'Teacher'
