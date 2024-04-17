from celery import shared_task
from django.core.management import call_command


@shared_task
def auto_assessment_task():
    call_command('auto_assessment')
