# Generated by Django 4.1.7 on 2023-03-12 10:55

import content_for_evrbd.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_for_evrbd', '0005_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quizzes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('quiz', models.FileField(upload_to=content_for_evrbd.models.content_quiz_name)),
                ('answer', models.FileField(upload_to=content_for_evrbd.models.content_quiz_name)),
            ],
        ),
    ]