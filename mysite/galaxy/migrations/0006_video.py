# Generated by Django 4.1.7 on 2023-03-05 13:16

from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0005_alter_customuser_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('url', embed_video.fields.EmbedVideoField()),
            ],
        ),
    ]