# context processors
from galaxy.models import TestsToCheck, CustomUser


def tests_to_check_notification(request):
    return {'tests_to_check': TestsToCheck.objects.filter(is_checked=False).count()}


def student_to_confirm_notification(request):
    return {'students_to_confirm': CustomUser.objects.filter(role='Student', is_confirmed=None).count()}
