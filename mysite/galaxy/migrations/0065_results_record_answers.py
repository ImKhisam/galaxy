# Generated by Django 4.1.7 on 2023-06-02 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0064_alter_results_detailed_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='record_answers',
            field=models.TextField(blank=True, max_length=600),
        ),
    ]