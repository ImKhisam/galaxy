from django.core.management.base import BaseCommand
from django.utils import timezone
from galaxy.models import Assessments


class Command(BaseCommand):
    help = 'Auto open and close assessments based on scheduled dates'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()

        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(current_date)

        # Auto close opened assessments
        opened_assessments = Assessments.objects.filter(is_opened=True, is_passed=False)
        opened_assessments.update(is_passed=True)

        # Auto open assessments scheduled for today
        assessments_to_open = Assessments.objects.filter(date=current_date)
        assessments_to_open.update(is_opened=True)

        self.stdout.write(self.style.SUCCESS('Assessments processed successfully.'))
