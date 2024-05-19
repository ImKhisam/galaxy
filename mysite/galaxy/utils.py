from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin

from galaxy.forms import *
from galaxy.models import CustomUser
from django.shortcuts import redirect
from datetime import date


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

            'GSESpeaking': '''Устная часть ОГЭ по английскому языку включает в себя 3 задания.
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

            'USEGrammar and Vocabulary': '''В разделе грамматики по ЕГЭ Вам предлагается выполнить 18 заданий на понимание прочитанных текстов.
                             Как только Вы попадете на страницу задания- запустится таймер для выполнения теста,
                             таймер не обнулится при обновлении страницы или выходе из личного кабинета. 
                             По истечении времени выполнение теста закончится автоматически. 
                             Задания, где Вы не укажете вариант ответа- он будет засчитан как неверный.''',

            'USESpeaking': '''Устная часть ЕГЭ по английскому языку включает в себя 4 задания.
                             Задание 1 – чтение вслух небольшого текста научно-популярного характера. Время на подготовку – 1,5 минуты.
                             В задании 2 предлагается ознакомиться с рекламным объявлением и задать четыре вопроса на основе ключевых слов. 
                             Время на подготовку – 1,5 минуты.
                             В задании 3 предлагается дать интервью на актуальную тему, развёрнуто и точно ответив на пять вопросов.
                             В задании 4 предлагается проблемная тема для проектной работы и 2 фотографии; 
                             нужно обосновать выбор фотографий в качестве иллюстраций и выразить своё мнение 
                             по проблеме проектной работы. Время на подготовку – 2,5 минуты.
                             Общее время ответа одного экзаменуемого (включая время на подготовку) – 17 минут.
                             Каждое последующее задание выдаётся после окончания выполнения предыдущего задания. 
                             Постарайтесь полностью выполнить поставленные задачи, старайтесь говорить ясно и чётко, 
                             не отходить от темы и следовать предложенному плану ответа. 
                             Так Вы сможете набрать наибольшее количество баллов. ''',

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
                              В ответе на задание 2 числительные пишите цифрами.''',
            'USEListening2': ''' Вы услышите интервью. В заданиях 3–9 выберите один из вариантов ответа.
                                 Вы услышите запись дважды.''',
            'USEReading2': '''Прочитайте текст и выполните задания 3–9. В каждом задании
                              выберите один из вариантов ответа.''',
            'USEGrammar and Vocabulary1': '''Прочитайте приведённые ниже тексты. Преобразуйте, если необходимо,
                                            слова, напечатанные заглавными буквами в конце строк, обозначенных
                                            номерами 1–6, так, чтобы они грамматически соответствовали
                                            содержанию текстов. Заполните пропуски полученными словами. Каждый
                                            пропуск соответствует отдельному заданию из группы 1–6. Помните, 
                                            что ответы нужно вводить ЗАГЛАВНЫМИ буквами.''',
            'USEGrammar and Vocabulary3': '''Прочитайте приведённый ниже текст. Образуйте от слов, напечатанных
                                             заглавными буквами в конце строк, обозначенных номерами 7–11,
                                             однокоренные слова так, чтобы они грамматически и лексически
                                             соответствовали содержанию текста. Заполните пропуски полученными
                                             словами. Каждый пропуск соответствует отдельному заданию из
                                             группы 7–11. Помните, что ответы нужно вводить ЗАГЛАВНЫМИ буквами.''',
            'USEGrammar and Vocabulary4': '''Прочитайте текст с пропусками, обозначенными номерами 12–18. Эти
                                             номера соответствуют заданиям 12–18, в которых представлены
                                             возможные варианты ответов. Выберите для каждого пропуска,
                                             соответствующий вариант ответа.''',
            'GSEListening1': '''Вы услышите четыре коротких текста, обозначенных буквами А, B, C, D.
                                В заданиях 1–4 выберите один из вариантов ответа. Вы услышите запись дважды.''',
            'GSEListening2': '''Вы помогаете своему другу, юному радиожурналисту, проанализировать
                                подготовленное им для передачи интервью. Прослушайте аудиозапись
                                интервью и занесите данные в поля для ответов. Вы можете вписать не более
                                одного слова (без артиклей) из прозвучавшего текста. Числа необходимо
                                записывать буквами. Вы услышите запись дважды.''',
            'GSEReading2': '''Прочитайте текст. Определите, какие из приведённых утверждений 2–8
                              соответствуют содержанию текста (1 – True), какие не соответствуют
                              (2 – False) и о чём в тексте не сказано, то есть на основании текста нельзя
                              дать ни положительного, ни отрицательного ответа (3 – Not stated).''',
            'GSEGrammar and Vocabulary1': '''Прочитайте приведённый ниже текст. Преобразуйте слова, напечатанные
                                             заглавными буквами в конце строк, обозначенных номерами 1–9, так,
                                             чтобы они грамматически соответствовали содержанию текста.
                                             Заполните пропуски полученными словами. Каждый пропуск соответствует
                                             отдельному заданию 1–9. Помните, что ответы нужно вводить ЗАГЛАВНЫМИ 
                                             буквами.''',
            'GSEGrammar and Vocabulary2': '''Прочитайте приведённый ниже текст. Преобразуйте слова, напечатанные
                                             заглавными буквами в конце строк, обозначенных номерами 10–15 так,
                                             чтобы они грамматически и лексически соответствовали содержанию
                                             текста. Заполните пропуски полученными словами. Каждый пропуск
                                             соответствует отдельному заданию 10–15. Помните, что ответы нужно вводить 
                                             ЗАГЛАВНЫМИ буквами.''',
            }

    def add_chapter_const_value(self, chapter_obj):
        key = chapter_obj.test_id.type + chapter_obj.test_id.part + str(chapter_obj.chapter_number)
        if key in self.info.keys():
            chapter_obj.info = self.info[key]
            chapter_obj.save()


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

    question_points = {'GSEListening5': 5,
                       'GSEReading1': 6,
                       'GSEWriting1': 10,
                       'GSESpeaking1': 2,
                       'GSESpeaking2': 6,
                       'GSESpeaking3': 7,
                       'USEListening1': 2,
                       'USEListening2': 3,
                       'USEReading1': 3,
                       'USEReading2': 2,
                       'USEWriting1': 6,
                       'USEWriting2': 14,
                       'USEWriting3': 14,
                       'USESpeaking1': 1,
                       'USESpeaking2': 4,
                       'USESpeaking3': 5,
                       'USESpeaking4': 10,
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
    def choose_form(self, type, chapter_object):
        key = type + ' ' + chapter_object.test_id.part
        dict = {'add Writing': AddWritingQandAForm,
                'add Speaking': AddSpeakingQandAForm,
                'add Listening': AddQuestionForm,
                'add Grammar and Vocabulary': AddQuestionForm,
                'add Reading': AddQuestionForm,
                'edit Writing': EditWritingQandAForm,
                'edit Speaking': EditSpeakingQandAForm,
                'edit Listening': EditQuestionForm,
                'edit Grammar and Vocabulary': EditQuestionForm,
                'edit Reading': EditQuestionForm,
                }
        return dict[key]


def teacher_check(user):
    return user.role == 'Teacher'


def form_assessment_dict(user_id):
    user = CustomUser.objects.get(id=user_id)
    user_assessment_dates = Assessments.objects \
        .filter(group=user.group, is_passed=True).order_by('date').distinct('date')
    assessment_dict = {x: Assessments.objects.filter(date=x.date) for x in user_assessment_dates}
    ordered_dict = {}
    right_order = ['Listening', 'Reading', 'Grammar and Vocabulary', 'Writing', 'Speaking']
    for key in assessment_dict:
        ordered_dict[key] = sorted(assessment_dict[key], key=lambda x: right_order.index(x.test.part))

    content_dict = {x: [Results.objects.get(test_id=y.test, student_id=user)
                        if Results.objects.filter(student_id=user, test_id=y.test).exists()
                        else "no result" for y in ordered_dict[x]]
                    for x in ordered_dict.keys()}

    # counting %
    for assessment_object, results in content_dict.items():
        if assessment_object.test.type == 'USE':
            max_points = 82
        else:
            max_points = 68
        while len(results) < 5:
            results.append('no result')
        cleared_list = [i for i in results if i != 'no result']
        sum_of_points = sum([int(result.points) for result in cleared_list])
        results.append(str(sum_of_points) + '(' + str(max_points) + ')')
        results.append(str(round(sum_of_points / (max_points / 100))) + '%')

    return content_dict


def get_max_points_dict():
    return {'GSEListening': '15',
            'GSEReading': '13',
            'GSEGrammar and Vocabulary': '15',
            'GSEWriting': '10',
            'GSESpeaking': '15',
            'USEListening': '12',
            'USEReading': '12',
            'USEGrammar and Vocabulary': '18',
            'USEWriting': '20',
            'USESpeaking': '20'}
