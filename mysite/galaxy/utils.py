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


class AddTestTimeLimit:
    dict = {'GSEListening': 30,
            'GSEReading': 30,
            'GSEGrammar and Vocabulary': 30,
            'GSESpeaking': 15,
            'GSEWriting': 30,
            'USEListening': 30,
            'USEReading': 30,
            'USEGrammar and Vocabulary': 40,
            'USESpeaking': 17,
            'USEWriting': 90}

    def add_test_time_limit(self, testobject):
        testobject.time_limit = self.dict[testobject.type + testobject.part]
        testobject.save()
