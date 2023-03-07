# Generated by Django 4.1.7 on 2023-03-07 09:31

from django.db import migrations, models
import galaxy.models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0006_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='BritishBulldog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classes', models.CharField(max_length=255, verbose_name='Class')),
                ('year', models.CharField(max_length=255, verbose_name='Year')),
                ('content', models.FileField(upload_to=galaxy.models.content_file_name)),
                ('audio', models.FileField(blank=True, upload_to=galaxy.models.content_file_name)),
            ],
            options={
                'ordering': ['year', 'classes'],
            },
        ),
        migrations.DeleteModel(
            name='Video',
        ),
    ]
