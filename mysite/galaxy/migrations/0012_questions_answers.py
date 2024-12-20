# Generated by Django 4.1.7 on 2023-03-15 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0011_alter_tests_part_alter_tests_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=600)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galaxy.tests')),
            ],
        ),
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=200)),
                ('is_true', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galaxy.questions')),
            ],
        ),
    ]
