# Generated by Django 4.1.7 on 2024-01-11 13:42

from django.db import migrations, models
import galaxy.models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0077_alter_questions_preparation_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='picture',
            field=models.FileField(blank=True, upload_to=galaxy.models.content_file_name_question),
        ),
    ]
