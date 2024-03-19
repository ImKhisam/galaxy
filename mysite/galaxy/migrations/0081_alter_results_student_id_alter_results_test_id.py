# Generated by Django 4.1.7 on 2024-03-18 20:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0080_results_test_to_check'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='student_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='results',
            name='test_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='galaxy.tests'),
        ),
    ]
