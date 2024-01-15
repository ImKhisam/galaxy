# Generated by Django 4.1.7 on 2023-10-31 09:14

from django.db import migrations, models
import galaxy.models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0075_alter_questions_preparation_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskstocheck',
            name='media1',
            field=models.FileField(blank=True, max_length=250, upload_to=galaxy.models.content_file_name_check),
        ),
        migrations.AlterField(
            model_name='taskstocheck',
            name='media2',
            field=models.FileField(blank=True, max_length=250, upload_to=galaxy.models.content_file_name_check),
        ),
    ]