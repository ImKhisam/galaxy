# Generated by Django 4.1.7 on 2023-06-05 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0065_results_record_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessments',
            name='is_passed',
            field=models.BooleanField(default=False),
        ),
    ]
