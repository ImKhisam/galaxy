# context processors
from galaxy.models import *
from django.utils.functional import SimpleLazyObject


def tests_to_check_notification(request):
    return {'tests_to_check': TestsToCheck.objects.filter(is_checked=False).count()}


def student_to_confirm_notification(request):
    return {'students_to_confirm': CustomUser.objects.filter(role='Student', is_confirmed=None).count()}


def current_assessments_notification(request):
    def complicated_query():
        current_user = CustomUser.objects.get(id=request.user.id)
        return Assessments.objects.filter(group=current_user.group, is_passed=False).count()

    return {
        'current_assessments_notification': SimpleLazyObject(complicated_query)}
