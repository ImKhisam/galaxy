# Generated by Django 4.1.7 on 2023-03-22 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0022_alter_results_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='time',
            field=models.CharField(max_length=50),
        ),
    ]
