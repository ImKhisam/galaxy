# Generated by Django 4.1.7 on 2023-03-15 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0012_questions_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='cost',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]