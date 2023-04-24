from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.db.models import Q

from galaxy.models import CustomUser


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_email_verified)


generate_token = TokenGenerator()


class ConfirmMixin:
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
        return CustomUser.objects.filter(role='Student', is_confirmed=value)


class AddTestConstValues:
    timings = {'GSEListening': 30,
            'GSEReading': 30,
            'GSEGrammar and Vocabulary': 30,
            'GSESpeaking': 15,
            'GSEWriting': 30,
            'USEListening': 30,
            'USEReading': 30,
            'USEGrammar and Vocabulary': 40,
            'USESpeaking': 17,
            'USEWriting': 90}

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

    def add_test_const_values(self, testobject):
        testobject.time_limit = self.timings[testobject.type + testobject.part]
        testobject.test_details = self.texts[testobject.type + testobject.part]
        testobject.save()
