# Generated by Django 4.1.7 on 2023-04-21 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0050_rename_test_info_tests_test_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='time_limit',
            field=models.PositiveIntegerField(blank=True, default=10),
            preserve_default=False,
        ),
    ]