# Generated by Django 4.1.7 on 2024-03-28 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0082_remove_customuser_assessments_passed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tests',
            name='order',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
