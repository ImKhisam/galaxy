# Generated by Django 4.1.7 on 2023-03-20 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0019_alter_results_result'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questions',
            old_name='cost',
            new_name='points',
        ),
        migrations.RenameField(
            model_name='results',
            old_name='result',
            new_name='points',
        ),
    ]
