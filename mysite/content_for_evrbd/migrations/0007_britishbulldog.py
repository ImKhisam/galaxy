# Generated by Django 4.1.7 on 2023-03-13 11:04

import content_for_evrbd.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_for_evrbd', '0006_britishbulldog_quizzes'),
    ]

    operations = [
        migrations.CreateModel(
            name='BritishBulldog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classes', models.CharField(max_length=255, verbose_name='Class')),
                ('year', models.CharField(max_length=255, verbose_name='Year')),
                ('content', models.FileField(upload_to=content_for_evrbd.models.content_bb_name)),
                ('audio', models.FileField(blank=True, upload_to=content_for_evrbd.models.content_bb_name)),
            ],
            options={
                'ordering': ['year', 'classes'],
            },
        ),
    ]
