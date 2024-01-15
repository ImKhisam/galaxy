# Generated by Django 4.1.7 on 2023-10-17 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0072_remove_questions_writing_before_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='text_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[(None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher')], default='Student', max_length=100),
        ),
    ]