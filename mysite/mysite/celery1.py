import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('galaxy')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-assessment-task': {
        'task': 'galaxy.tasks.auto_assessment_task',
        'schedule': crontab(hour=0, minute=1),  # Run at midnight every day
    },
}
