# Generated by Django 2.2.24 on 2022-03-08 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appearance', '0005_theme_fontlink'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='fontLink',
        ),
    ]
