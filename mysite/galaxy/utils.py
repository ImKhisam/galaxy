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
