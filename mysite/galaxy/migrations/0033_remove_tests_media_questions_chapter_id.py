# Generated by Django 4.1.7 on 2023-03-29 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0032_chapters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tests',
            name='media',
        ),
        migrations.AddField(
            model_name='questions',
            name='chapter_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='galaxy.chapters'),
            preserve_default=False,
        ),
    ]
