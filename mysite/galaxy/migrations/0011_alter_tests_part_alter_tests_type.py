# Generated by Django 4.1.7 on 2023-03-13 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0010_tests_test_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tests',
            name='part',
            field=models.CharField(choices=[('Listening', 'Listening'), ('Reading', 'Reading'), ('Grammar and Vocabulary', 'Grammar'), ('Writing', 'Writing'), ('Speaking', 'Speaking')], max_length=255, verbose_name='Part of exam'),
        ),
        migrations.AlterField(
            model_name='tests',
            name='type',
            field=models.CharField(choices=[('GSE', 'GSE'), ('USE', 'USE')], max_length=255, verbose_name='Type of exam'),
        ),
    ]
