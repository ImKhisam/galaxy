# Generated by Django 4.1.7 on 2023-03-24 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0027_remove_answers_match_answers_addition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='answers',
            name='match',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
