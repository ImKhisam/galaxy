from celery import shared_task, app
from django.core.management import call_command
from django.core.mail import send_mail


@shared_task
def auto_assessment_task():
    call_command('auto_assessment')


@shared_task
def send_assessment_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        None,
        recipient_list,
        fail_silently=False,
    )
